# search.py

class SearchExpr(object):
    def __init__(self, operator, *operands):
        self.operator = operator
        self.operands = operands

    def __and__(self, other):
        return SearchExpr('and', self, other)

    def __or__(self, other):
        return SearchExpr('or', self, other)

    def _collect(self):
        # ASSUME: At term level, we only have assoc binary operators (and, or)
        #   Be careful when XOR or something enters the picture!
        #   Modifies self!
        oo = []
        for o in [o._collect() for o in self.operands]:
            if o.operator == self.operator:
                oo = oo + list(o.operands)
            else:
                oo = oo + [o,]
        self.operands = oo
        return self
    
    def _render(self):
        return '(:' +  ' '.join( [self.operator,] + [o._render() for o in self.operands] ) + ')'

    def _pprint(self, prfix=''):
        return prfix + '(:' + self.operator + "\n" + \
            '\n'.join([o._pprint(prfix+'  ') for o in self.operands]) + ')'

class SearchTerm(SearchExpr):
    def _render(self):
        # NOTE: assumes operand[1..] to be "constants"
        return '(:%s %s %s)' % (self.operator,
                               self.operands[0]._render(),
                               ' '.join([repr(o) for o in self.operands[1:]]))

    def _pprint(self, prfix=''):
        return prfix + self._render()

    def _collect(self):
        # nothing to do
        return self

class SearchVar(object):
    def __init__(self, name, namespace):
        self.name = name
        self.namespace = namespace

    def __lt__(self, other):
        return SearchTerm('lt', self, other)

    def __le__(self, other):
        return SearchTerm('le', self, other)

    def __eq__(self, other):
        return SearchTerm('eq', self, other)

    def __ge__(self, other):
        return SearchTerm('ge', self, other)

    def __gt__(self, other):
        return SearchTerm('gt', self, other)

    def __ne__(self, other):
        return SearchTerm('ne', self, other)

    def range(self, lower, upper):
        return SearchTerm('range', self, lower, upper)

    def bind(self, symbol):
        return SearchTerm('bind', self, symbol)

    def _render(self):
        return '(%s %s)' % (self.namespace, self.name)
