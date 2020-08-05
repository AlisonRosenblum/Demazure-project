#!/usr/bin/env python3
from string import ascii_lowercase
import pandas

def identify_n(word):
    """
    identifies the minimal n for which word is in $S_n$

    Parameters
    ----------
    word : list or tuple
        elements refer to generators $s_1,s_2,...$

    Returns
    ----------
    n : int
        one greater than the largest integer appearing in word

    Examples
    ----------
    >>> identify_n((1,0,1,2))
    3

    >>> identify_n([1,2,3,4,5,4,3])
    6
    """
    return max(word)+1

def ob_join(separated):
    """
    joins a list of objects into a single object

    Paramenters
    ----------
    separated : list
        all elements strings

    Returns
    ----------
    str
        the concatenation of the strings in separated

    Examples
    ----------
    >>> ob_join(['a','b','c','d'])
    'abcd'
    """
    joined = ""
    for i in separated:
        joined += i
    return joined

def standard_product(word, n=None):
    """
    if word = $(i_1,\ldots,i_d)$, performs $s_{i_1}\circ\cdots\circs_{i_d}(abcd...)$

    Parameters
    ----------
    word : list or tuple
        the generators whose prodct to take

    n : int (optional)
        S_n in which the product will take place
        defaults to the smallest possible n

    Returns
    ----------
    str
        the element of S_n corresponding to the product of the generators in word
        (as the left action of the generators on abcd...)

    Examples
    ----------
    >>> standard_product([1])
    'ba'

    >>> standard_product([1],4)
    'bacd'

    >>> standard_product((3,2,1))
    'bcda'
    """
    if n == None:
        n = identify_n(word)

    to_apply = list(word)
    to_apply.reverse()
    element = list(ascii_lowercase[:n])
    for i in to_apply:
        if i < 0 or i >= n:
            raise ValueError("{} not between 0 and {}".format(i,n))
        if i==0:
            pass
        else:
            element[i-1],element[i]=element[i],element[i-1]
    return ob_join(element)

def create_element_cache(n):
    """
    creates a csv containing a list of elements of S_n

    Paramenters
    ----------
    n : int

    Returns
    ----------
    str
        name of the file where the data is stored

    Raises
    ----------
    ValueError
        if n is less than 2

    NotImplementedError
        if n is greater than 26
    """
    if not isinstance(n,int):
        raise TypeError("n must be an integer")
    if n < 2:
        raise ValueError("n must be greater than 2")
    if n > 26:
        raise NotImplementedError("module only implemented for $n\leq 26$")

    dim = sum(range(n))
    S_n = pandas.DataFrame([[ascii_lowercase[:n],0,[]]], columns = ["element","length","word"])
    S_n = S_n.set_index("element")
    for length in range(dim):
        build_from = S_n.loc[S_n.loc[:,"length"] == length]
        for old_element in build_from.index:
            old_word = list(S_n.at[old_element,"word"])
            for i in range(1,n):
                new_word = old_word+[i]
                new_element = standard_product(new_word,n)
                if new_element in S_n.index:
                    pass
                else:
                    S_n = S_n.append(pandas.Series(data={"length":length+1,"word":new_word},
                        name = new_element))
    return S_n
create_element_cache(3)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
