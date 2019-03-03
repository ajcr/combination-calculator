from collections import Counter
from typing import Dict, Sequence, List, Tuple, Hashable, Optional

from sympy import laguerre, assoc_laguerre, prod, factorial, Rational, Poly
from sympy.abc import x

from ccc.errors import ConstraintNotImplementedError


class PermutationCounter:
    """
    Count constrained permutations of a sequence.

    """
    def __init__(
        self,
        sequence: Sequence[Hashable],
        constraints: Optional[List[Tuple]] = None,
    ) -> None:

        self.frequencies: Counter = Counter(sequence)
        self.length: int = len(sequence)
        self.constraints: List[Tuple] = constraints
        self.polynomials: Dict[Hashable, Poly] = {}

        if not constraints:
            pass

        elif len(constraints) == 1:
            op, *args = constraints[0]
            getattr(self, "impose_constraint_" + op)(*args)

        else:
            raise ConstraintNotImplementedError("Imposing multiple constraints is not supported")

    def impose_constraint_derangement(self) -> None:
        """
        Permutation has no items in their original position.

        Uses the Laguerre polynomial approach detailed in
        "Derangements and Laguerre polynomials", S. Even & J. Gillis,
        Mathematical Proceedings of the Cambridge Philosophical Society,
        Volume 79, Issue 1 January 1976 , pp. 135-143.

        """
        for item, count in self.frequencies.items():
            self.polynomials[item] = laguerre(count, x)

    def impose_constraint_no_adjacent(self) -> None:
        """
        Permutation has no consecutive items equal to each other.

        Uses the generalised Laguerre polynomial approach detailed in
        "Counting words with Laguerre series", J. Taylor, The Electronic
        Journal of Combinatorics (E-JC), Volume 21, Issue 2 (2014).

        (https://www.combinatorics.org/ojs/index.php/eljc/article/view/v21i2p1)

        """
        for item, count in self.frequencies.items():
            self.polynomials[item] = assoc_laguerre(count, -1, x)

    def count_unconstrained_permutations(self) -> int:
        """
        Number of permutations where no constraint is specified.

        If a, b, ..., n are the counts of each item in the sequence,
        this is equal to:

            len(sequence)! / a! / b! / ... /n!

        """
        return factorial(self.length) / prod(factorial(a) for a in self.frequencies.values())

    def probability(self) -> Rational:
        """
        Probability that a permutation of the sequence meets the
        specified contraints.
        """
        return self.count() / self.count_unconstrained_permutations()

    def count(self) -> int:
        """
        Number of permutations of the sequence that meets the
        specified contraints.
        """
        if not self.constraints:
            return self.count_unconstrained_permutations()

        else:
            terms = prod(self.polynomials.values()).apart().as_ordered_terms()
            return abs(sum(eval_gamma(t) for t in terms))


def eval_gamma(term):
    """
    Evaluate the term k*x**n as k*n!
    """
    coeff, exp = term.as_coeff_exponent(x)
    return coeff * factorial(exp)
