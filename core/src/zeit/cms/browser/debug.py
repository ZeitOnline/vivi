import guppy


hpy = guppy.hpy()


class Refcount:

    def refcount(self, amount=None):
        result = []

        hp = hpy.heap()
        result.append(str(hp))

        for x in range(3):
            rcs = hp[0].byrcs
            result.append(str(rcs))
            hp = rcs

        return '\n\n'.join(result)
