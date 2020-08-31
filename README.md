# Demazure Project

Tools in python for working with Demazure products and related tasks

## Motivation

This module contains tools for computing examples related to a current research
project, which seeks to extend the work of Davis, Hersh, and Miller described in
"[Fibers of Maps to Totally Nonnegative Spaces](https://arxiv.org/abs/1903.01420),"
focusing here exclusively on type A. Specific utilities include

- computing the Demazure product of a tuple of generators
- computing the map f_(i_1,\ldots,i_d) from R^d_{>= 0} to SL(n, R) for a
  provided word (i_1,...,i_d), and evaluating it at a given point
- finding the subwords of a given word that mulitply to a given element of S_n
  under the Demazure product
- for a given word (i_1,...,i_d), finding all elements w of S_n for which
  some non-reduced subword of (i_1,...,i_d) mulitplies to w under the
  Demazure product

This project served as the final project for the graduate course
"[Fundamentals of Programming for Mathematicians](https://www.math.purdue.edu/~bradfor3/ProgrammingFundamentals/)", and so is intended also as a demonstration of introductory
knowledge of a large proportion of the skills taught in that course.

## How-To

This code is currently equipped to function as a python module, with eventual intended
bash and web app interfaces.

The S_n.sqlite file contains data on the elements of S_n for a few small n. The
Lengths table contains a list of elements of S_n by n, along with the length of
each element. The Words table contains all reduced words for each element. The
database is set to populate automatically as needed, adding all data for a given n
when called upon by another function, should that information not already be present.
Computation time will increase significantly with n; but after the table is initialized
for a given n, the information will remain for much quicker retrieval in subsequent
uses. One can read from or write to this folder directly with SQL queries. Caution is
advised in the latter case; if irreparable damage does occur, though, the file may
be deleted entirely; the code will handle the creation of a clean (empty) database
if needed.

## Notation

This section of the readme contains a few brief definitions and explanations of
some terms and usages, the readers understanding of which is taken for granted
in the docstrings.

Adapted from "Combinatorics of Coxeter Groups" by Bjorner and Brenti:

A **Coxeter system** is a group W and a set of generators S of W conforming to certain
properties. Here, our group is the symmetric group S_n, and our generators are the
adjacent transpositions s_1=(1 2), s_2=(2 3), ... , s_{n-1}=(n-1 n).

If for an element w in W, the product s_{i_1}\cdots s_{i_d}=w, then we say that
s_{i_1}\cdots s_{i_d} is an **expression** for w, and call (i_1,\ldots,i_d) a
**word** for w. We will sometimes adopt the (non-standard) convention that words
may contain place-holding zeroes but expressions do not, but in practice will favor the
abbreviated word notation both for words and expressions.

The **length** of an element w in W, denoted l(w), is the smallest d such that
w=s_{i_1}\cdots s_{i_d} for some s_{i_1}, ... ,s_{i_d} in S. We will say (again
non-standardly) that the **expression length** of an expression s_{i_1}\cdots s_{i_d}
is d, and that for a word Q=(i_1, ... ,i_d), the **word length** of Q is d and the
expression length of Q is the number of non-zero integers among i_1, ..., i_d. An
expression is **reduced** if its expression length is equal to the length of the
element to which it mulitplies.

Adapted from "Introduction to Total Positivity" by Lusztig:

Let G be a semisimple algebraic group defined and split over the real numbers. If
(e_i,f_i,h_i) are Chevalley generators of the Lie algebra of G, we define for each e_i
a map **x_i** from the real numbers to G by x_i(t)=exp(te_i). In our case, where
G=SL(n,R), this translates to x_i(t)=Id_n +tE_{i,i+1} (the matrix with ones on the
diagonal, t in position i,i+1, and zeroes elsewhere). See docstrings for more concrete examples.

For a word (i_1, ..., i_d), define a map **f_(i_1,...,i_d)** from R^d to G by
f_(i_1,...,i_d)(t_1,...,t_d)=x_{i_1}(t_1)\cdots x_{i_d}(t_d), taking x_0=Id. This
module ultimately hopes to aid in the study of the properties of these maps.

Taken from "Fibers of Maps to Totally Nonnegative Spaces" by Davis, Hersh, and Miller:

The **Demazure product** of a group element w and a generator s is given by
    ws if l(ws)>l(w)
    w if l(ws)<l(w)
There is a unique associative extension of this product, by which we define the
d-fold Demazure product of a tuple of generators. For examples, see the docstrings.
