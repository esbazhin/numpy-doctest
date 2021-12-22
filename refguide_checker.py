import doctest
import numpy as np
import re


CHECK_NAMESPACE = {
      'np': np,
      'assert_allclose': np.testing.assert_allclose,
      'assert_equal': np.testing.assert_equal,
      # recognize numpy repr's
      'array': np.array,
      'matrix': np.matrix,
      'masked_array': np.ma.masked_array,
      'int64': np.int64,
      'uint64': np.uint64,
      'int8': np.int8,
      'int32': np.int32,
      'float32': np.float32,
      'float64': np.float64,
      'dtype': np.dtype,
      'nan': np.nan,
      'NaN': np.nan,
      'inf': np.inf,
      'Inf': np.inf }


class Checker(doctest.OutputChecker):
    obj_pattern = re.compile(r'at 0x[0-9a-fA-F]+>')
    vanilla = doctest.OutputChecker()
    rndm_markers = {'# random', '# Random', '#random', '#Random', "# may vary"}
    stopwords = {'plt.', '.hist', '.show', '.ylim', '.subplot(',
                 'set_title', 'imshow', 'plt.show', '.axis(', '.plot(',
                 '.bar(', '.title', '.ylabel', '.xlabel', 'set_ylim', 'set_xlim',
                 '# reformatted', '.set_xlabel(', '.set_ylabel(', '.set_zlabel(',
                 '.set(xlim=', '.set(ylim=', '.set(xlabel=', '.set(ylabel='}

    def __init__(self, parse_namedtuples=True, ns=None, atol=1e-8, rtol=1e-2):
        self.parse_namedtuples = parse_namedtuples
        self.atol, self.rtol = atol, rtol
        if ns is None:
            self.ns = dict(CHECK_NAMESPACE)
        else:
            self.ns = ns

    def check_output(self, want, got, optionflags):
        # cut it short if they are equal
        # return False

        if want == got:
            return True

        # skip stopwords in source
        # if any(word in self._source for word in self.stopwords):
        #     return True

        # skip random stuff
        if any(word in want for word in self.rndm_markers):
            return True

        # skip function/object addresses
        if self.obj_pattern.search(got):
            return True

        # ignore comments (e.g. signal.freqresp)
        if want.lstrip().startswith("#"):
            return True

        # try the standard doctest
        try:
            if self.vanilla.check_output(want, got, optionflags):
                return True
        except Exception:
            pass

        # OK then, convert strings to objects
        try:
            a_want = eval(want, dict(self.ns))
            a_got = eval(got, dict(self.ns))
        except Exception:
            # Maybe we're printing a numpy array? This produces invalid python
            # code: `print(np.arange(3))` produces "[0 1 2]" w/o commas between
            # values. So, reinsert commas and retry.
            # TODO: handle (1) abberivation (`print(np.arange(10000))`), and
            #              (2) n-dim arrays with n > 1
            s_want = want.strip()
            s_got = got.strip()
            cond = (s_want.startswith("[") and s_want.endswith("]") and
                    s_got.startswith("[") and s_got.endswith("]"))
            if cond:
                s_want = ", ".join(s_want[1:-1].split())
                s_got = ", ".join(s_got[1:-1].split())
                return self.check_output(s_want, s_got, optionflags)

            # maybe we are dealing with masked arrays?
            # their repr uses '--' for masked values and this is invalid syntax
            # If so, replace '--' by nans (they are masked anyway) and retry
            if 'masked_array' in want or 'masked_array' in got:
                s_want = want.replace('--', 'nan')
                s_got = got.replace('--', 'nan')
                return self.check_output(s_want, s_got, optionflags)

            if "=" not in want and "=" not in got:
                # if we're here, want and got cannot be eval-ed (hence cannot
                # be converted to numpy objects), they are not namedtuples
                # (those must have at least one '=' sign).
                # Thus they should have compared equal with vanilla doctest.
                # Since they did not, it's an error.
                return False

            if not self.parse_namedtuples:
                return False
            # suppose that "want"  is a tuple, and "got" is smth like
            # MoodResult(statistic=10, pvalue=0.1).
            # Then convert the latter to the tuple (10, 0.1),
            # and then compare the tuples.
            try:
                got_again = try_convert_namedtuple(got)
                want_again = try_convert_namedtuple(want)
            except Exception:
                return False
            else:
                return self.check_output(want_again, got_again, optionflags)


        # ... and defer to numpy
        try:
            return self._do_check(a_want, a_got)
        except Exception:
            # heterog tuple, eg (1, np.array([1., 2.]))
            try:
                return all(self._do_check(w, g) for w, g in zip(a_want, a_got))
            except (TypeError, ValueError):
                return False

    def _do_check(self, want, got):
        # This should be done exactly as written to correctly handle all of
        # numpy-comparable objects, strings, and heterogeneous tuples
        try:
            if want == got:
                return True
        except Exception:
            pass
        return np.allclose(want, got, atol=self.atol, rtol=self.rtol)


def try_convert_namedtuple(got):
    # suppose that "got" is smth like MoodResult(statistic=10, pvalue=0.1).
    # Then convert it to the tuple (10, 0.1), so that can later compare tuples.
    num = got.count('=')
    if num == 0:
        # not a nameduple, bail out
        return got
    regex = (r'[\w\d_]+\(' +
             ', '.join([r'[\w\d_]+=(.+)']*num) +
             r'\)')
    grp = re.findall(regex, got.replace('\n', ' '))
    # fold it back to a tuple
    got_again = '(' + ', '.join(grp[0]) + ')'
    return got_again
