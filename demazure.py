#!/usr/bin/env python3

import sqlite3
import numpy
import sympy.matrices
import pandas
from string import ascii_lowercase
from os import path
from csv import writer
from sympy import symbols


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
    if word == []:
        return 1
    else:
        return max(word)+1

def str_join(separated):
    """
    joins a list of strings into a single string

    Parameters
    ----------
    separated : list
        all elements strings

    Returns
    ----------
    str
        the concatenation of the strings in separated

    Examples
    ----------
    >>> str_join(['a','b','c','d'])
    'abcd'

    >>> str_join(['abc','d','ef'])
    'abcdef'
    """
    joined = ""
    for i in separated:
        joined += i
    return joined

def standard_product(word, n=None):
    """
    if word = $(i_1,\ldots,i_d)$, performs $s_{i_1}\circ\cdots\circ s_{i_d}(abcd...)$

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
    return str_join(element)

def x(i,t=symbols("t"),n=None):
    """
    creates the matrix x_i(t) (n-dimensional)

    Parameters
    ----------
    i : int
        the generator this matrix corresponds to

    t : symbol or int or float
        the value at which to evaluate x_i(t)

    n : int (optional)
        the dimension of the matrix
        if None, autodetects from i (not recommended)

    Returns
    ----------
    sympy.matrices.dense.MutableDenseMatrix
        the matrix representing x_i(t) in dimension n

    Examples
    ----------
    >>> x(2,4.5)
    Matrix([
    [1, 0,   0],
    [0, 1, 4.5],
    [0, 0,   1]])

    >>> x(1,n=3)
    Matrix([
    [1, t, 0],
    [0, 1, 0],
    [0, 0, 1]])
    """
    if n == None:
        n = identify_n([i])
    if i<0 or i>=n:
        raise ValueError("i must be between 0 and n")

    s = sympy.eye(n)
    if i == 0:
        return s
    s[i-1,i] = t
    return s

def f_w(word, n = None, point = None):
    """
    creates the matrix giving f_(i_1,\ldots,i_d)(t_1,\ldots,t_d)

    Parameters
    ----------
    word : list or tuple
        the word defining this map

    n : int (optional)
        the dimension of the matrix output
        if None, autodetects dimension

    point : list or tuple (optional)
        a point in $R^d$ at which to evaluate the function

    Returns
    ----------
    sympy.matrices.dense.MutableDenseMatrix :
    the matrix giving f_w(t) or f_w(a) if a is supplied, in dimension n

    Examples
    ----------
    >>> f_w([1,2,1])
    Matrix([
    [1, t_1 + t_3, t_1*t_2],
    [0,         1,     t_2],
    [0,         0,       1]])

    >>> f_w([2,1], n=4, point=[symbols('x'),symbols('y')])
    Matrix([
    [1, y, 0, 0],
    [0, 1, x, 0],
    [0, 0, 1, 0],
    [0, 0, 0, 1]])

    >>> f_w([4,1,2,4], point=[1,2,3,4])
    Matrix([
    [1, 2, 6, 0, 0],
    [0, 1, 3, 0, 0],
    [0, 0, 1, 0, 0],
    [0, 0, 0, 1, 5],
    [0, 0, 0, 0, 1]])
    """
    if n == None:
        n = identify_n(word)

    t = [sympy.symbols("t_{}".format(j+1)) for j in range(len(word))]
    f = sympy.eye(n)
    for i in range(len(word)):
        f *= x(word[i],t[i],n)
    if point != None:
        subs_dict = {}
        for i in range(len(word)):
            subs_dict[t[i]] = point[i]
        f = f.subs(subs_dict)
    return f

def obtain_db_name():
    """
    obtains the input needed to access the database storing the elements of S_n

    Returns
    ----------
    str :
        the relative path name for S_n.sqlite
    """
    #for testing
    if __name__ == "__main__":
        return "S_n.sqlite"

    path_name = __file__[:__file__.find("demazure.py")-1]
    rel_path_name = path.relpath(path_name)
    return path.join(rel_path_name,"S_n.sqlite")

def create_element_cache(n):
    """
    creates a csv containing a list of elements of S_n

    Paramenters
    ----------
    n : int

    Returns
    ----------
    bool
        true if completed successfully,
        false if database already initialized for this n

    Raises
    ----------
    ValueError
        if n is less than 1

    NotImplementedError
        if n is greater than 26
    """
    if not isinstance(n,int):
        raise TypeError("n must be an integer")
    if n < 1:
        raise ValueError("n must be greater than 1")
    if n > 4:
        print("Creating cache. This may take a while...")
    if n > 26:
        raise NotImplementedError("module only implemented for $n\leq 26$")
    dim = sum(range(n))

    #create table in database
    db_name = obtain_db_name()
    with sqlite3.connect(db_name) as conn:
        cur = conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS Lengths (
            element TEXT PRIMARY KEY,
            n_value INT,
            length INT
        )
        """)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS Words (
            element TEXT,
            n_value INT,
            word TEXT,
            PRIMARY KEY (word,n_value),
            FOREIGN KEY (element) REFERENCES Lengths(element),
            FOREIGN KEY (n_value) REFERENCES Lengths(n_value)
        )
        """)
        conn.commit()

    #initialize tables
    try:
        with sqlite3.connect(db_name) as conn:
            cur = conn.cursor()
            cur.execute("""
            INSERT INTO Lengths (
                n_value,
                element,
                length
            )
            VALUES (?,?,?)
            """,(n,ascii_lowercase[:n],0))
            cur.execute("""
            INSERT INTO Words (
                n_value,
                element,
                word
            )
            VALUES (?,?,?)
            """,(n,ascii_lowercase[:n],""))
            conn.commit()
    except sqlite3.IntegrityError:
        return False

    #loop to fill table
    for length in range(dim):
        with sqlite3.connect(db_name) as conn:
            cur = conn.cursor()
            cur.execute("""
            SELECT element
            FROM Lengths
            WHERE n_value = ? AND length = ?
            """,(n,length-1))
            check = [i[0] for i in cur.fetchall()]
        with sqlite3.connect(db_name) as conn:
            cur = conn.cursor()
            cur.execute("""
            SELECT element
            FROM Lengths
            WHERE n_value = ? and length = ?
            """,(n,length))
            build = [i[0] for i in cur.fetchall()]
        for old_element in build:
            with sqlite3.connect(db_name) as conn:
                cur = conn.cursor()
                cur.execute("""
                SELECT word
                FROM Words
                WHERE n_value = ? and element = ?
                """,(n,old_element))
                old_words = [i[0] for i in cur.fetchall()]
            for word in old_words:
                word = word.split(",")
                if word == [""]:
                    word = []
                word = [int(j) for j in word]
                for i in range(1,n):
                    new_word = word + [i]
                    new_element = standard_product(new_word,n)
                    if new_element in check:
                        pass
                    else:
                        try:
                            with sqlite3.connect(db_name) as conn:
                                cur = conn.cursor()
                                cur.execute("""
                                INSERT INTO Lengths (
                                    n_value,
                                    element,
                                    length
                                )
                                VALUES (?,?,?)
                                """,(n,new_element,length+1))
                                conn.commit()
                        except sqlite3.IntegrityError:
                            pass
                        new_word = [str(j)+"," for j in word]+[str(i)]
                        new_word = str_join(new_word)
                        try:
                            with sqlite3.connect(db_name) as conn:
                                cur = conn.cursor()
                                cur.execute("""
                                INSERT INTO Words (
                                    n_value,
                                    element,
                                    word
                                )
                                VALUES (?,?,?)
                                """,(n,new_element,new_word))
                                conn.commit()
                        except sqlite3.IntegrityError:
                            pass
    return True

def demazure_product(word,n=None):
    """
    computes the Demazure product of the elements of word

    Parameters
    ----------
    word : list or tuple
        the generators whose Demazure product to take

    Returns
    --------
    new_word : list
        the product as a list

    Notes
    ----------
    the Demazure product of a group element w and a generator s is given by
        ws if l(ws)>l(w)
        w if l(ws)<l(w)
    (where l(w) is the length of the element w)
    d-fold products are the unique associative extension of this product.

    Examples
    ----------
    >>> demazure_product([1,1,1,1],2)
    [1]

    >>> demazure_product([1,2,1,2])
    [1, 2, 1]

    >>> demazure_product([1,2,3])
    [1, 2, 3]
    """
    if n == None:
        n = identify_n(word)
    db_name = obtain_db_name()

    #check if S_n.sqlite has been filled for this n
    with sqlite3.connect(db_name) as conn:
        cur = conn.cursor()
        cur.execute("""
        SELECT element
        FROM Lengths
        WHERE (n_value = ? AND length = ?)
        """,(n,0))
        check_existance = cur.fetchall()
    if check_existance == []:
        create_element_cache(n)

    if word == []:
        return [[],ascii_lowercase[:n]]
    start = 0
    while (word[start] == 0 and start < len(word)-1):
        start += 1
    product_word = [word[start]]
    for i in word[(start+1):]:
        old_element = standard_product(product_word,n)
        with sqlite3.connect(db_name) as conn:
            cur = conn.cursor()
            cur.execute("""
            SELECT length
            FROM Lengths
            WHERE (n_value = ? AND element = ?)
            """,(n,old_element))
            old_length = cur.fetchall()[0][0]
        new_element = standard_product(product_word + [i],n)
        with sqlite3.connect(db_name) as conn:
            cur = conn.cursor()
            cur.execute("""
            SELECT length
            FROM Lengths
            WHERE (n_value = ? AND element = ?)
            """,(n,new_element))
            new_length = cur.fetchall()[0][0]
        if old_length < new_length:
            product_word = product_word + [i]
    return product_word

def subword(pos_data):
    """
    selects the ith subword of a word

    Parameters
    ----------
    pos_data : tuple
        (word, i) where word is the word whose subwords to find and i is the
        index of the subword (in a list of binary digits)

    Returns
    ----------
    list
        the ith subword

    Raises
    ----------
    NotImplementedError
        if the wordlength exceeds 63

    Examples
    ----------
    >>> subword(([1,1,1],3))
    [1, 1, 0]

    >>> subword(([4,1,2,3],11))
    [4, 1, 0, 3]
    """
    word,i=pos_data
    wordlength = len(word)
    if wordlength >= 64:
        raise NotImplementedError("The word-length is too large")
    word = numpy.array(word)

    subword = numpy.ones((wordlength),numpy.int8)
    places = 2*numpy.ones((wordlength),numpy.uint64)
    places = places**numpy.arange(wordlength).astype(numpy.uint64)
    subword = (i*subword//places)%2
    subword = (subword*word).astype(numpy.int32)
    subword_py = [int(i) for i in subword]
    return subword_py

def subword_element_association(word, n=None):
    """
    determines the element associated with each subword of a word

    Parameters
    ----------
    word : list
        the word whose subwords to find

    n : int (optional)
        S_n in which word lives (autodetects if None)

    Returns
    ----------
    pandas.DataFrame
        contains all subwords, and their corresponding elements

    Examples
    ----------
    >>> subword_element_association([1,2])
      subwords element
    0   [0, 0]     abc
    1   [1, 0]     bac
    2   [0, 2]     acb
    3   [1, 2]     cab
    """
    if n == None:
        n = identify_n(word)

    subwords = pandas.Series([(word,i) for i in range(2**len(word))],name="subwords")
    subwords = subwords.map(subword)
    elements = pandas.Series(subwords.map(demazure_product),name="element")
    elements = elements.apply(standard_product,n=n)
    sws_to_elements = pandas.DataFrame(subwords)
    sws_to_elements = sws_to_elements.join(elements)
    return sws_to_elements

def calculate_expression_length(word):
    """
    calculates the expression length (number of non-zero elements) for a given word

    Parameters
    ----------
    word : list
        the word whose expression length to calculate

    Returns
    ----------
    int
        the expression length of word

    Examples
    ----------
    >>> calculate_expression_length([1,1,1])
    3

    >>> calculate_expression_length([])
    0

    >>> calculate_expression_length([0])
    0

    >>> calculate_expression_length([0,1,0,1,0])
    2
    """
    expression = [i for i in word if i != 0]
    return len(expression)

def process_element(subword_table, element):
    """
    slices a table of words to those multiplying to a given element
    also indicates which words are reduced

    Parameters
    ----------
    subword_table : pandas.DataFrame
        contains all subwords of some word, and the elements they mulitply to under the Demazure product

    element : string
        the element to search for

    Returns
    ----------
    pandas.DataFrame
        contains the subwords that multiply to element, and an indication of whether
        each subword is reduced

    Raises
    ----------
    ValueError
        if expression is not an element of S_n

    Examples
    ----------
    >>> process_element(pandas.DataFrame([[[0,0],"abc"],[[1,0],"bac"],[[0,1],"bac"],[[1,1],"bac"]],
    ...    columns = ["subwords","element"]),"bac")
      elements  reduced
    1   [1, 0]     True
    2   [0, 1]     True
    3   [1, 1]    False

    >>> process_element(pandas.DataFrame([[[0,0],"abc"],[[1,0],"bac"],[[0,1],"bac"],[[1,1],"bac"]],
    ...    columns = ["subwords","element"]),"acb")
    Empty DataFrame
    Columns: [elements, reduced]
    Index: []
    """
    element_sws = subword_table.loc[subword_table.loc[:,"element"] == element,"subwords"]
    element_sws = pandas.Series(element_sws, name="elements")
    db_name = obtain_db_name()
    with sqlite3.connect(db_name) as conn:
        cur = conn.cursor()
        cur.execute("""
        SELECT length
        FROM Lengths
        WHERE element = ?
        """,(element,))
        element_length = cur.fetchall()
    if element_length == []:
        raise ValueError("{} not in S_n".format(element))
    else:
        element_length = element_length[0][0]
    expression_lengths = element_sws.map(calculate_expression_length)
    reduced = pandas.Series(expression_lengths == element_length,name="reduced")
    element_sws = pandas.DataFrame(element_sws)
    element_sws = element_sws.join(reduced)
    return element_sws

def element_subwords(word,element,filename=None):
    """
    finds all subwords of word that multiply to element under the Demazure product
    indicates if said subword is a reduced word for the element

    Parameters
    ----------
    word : list
        the word whose subwords to search

    element : str
        the element of S_n to which the subwords should multiply

    filename : str (optional)
        the file in which to store the data
        if None, returns data as a string

    Returns
    ----------
    str :
        filename if given
        otherwise, the data as a string

    Examples
    ----------
    >>> print(element_subwords([1,2,1],"bac"))
    bac
      elements  reduced
     [1, 0, 0]     True
     [0, 0, 1]     True
     [1, 0, 1]    False
    """
    n = len(element)
    subwords = subword_element_association(word,n)
    slice = process_element(subwords,element)

    if filename == None:
        report = element + "\n"
        report += slice.to_string(index=False)
        return report
    else:
        with open(filename, "w") as f:
            write = writer(f)
            write.writerow([element])
        slice.to_csv(filename,index=False,mode="a")
        return filename

def non_trivial_subwords(word,n=None,filename=None):
    """
    produces a list of all elements mulitplied to by a nonreduced subword of word
    includes all subwords mulitplying to each of these elements under the Demazure
    product, and indications of which are reduced

    Parameters
    ----------
    word : list
        the word whose subwords to search

    n : int (optional)
        S_n in which the word lives
        if None, autodetects (not recommended)

    filename : str (optional)
        the file in which to store the data
        if None, returns as a string

    Returns
    ----------
    str
        filename if given
        otherwise, the data as a string

    Examples
    ----------
    >>> print(non_trivial_subwords([1,3,1]))
    In [1, 3, 1]:
    <BLANKLINE>
    bacd
      elements  reduced
     [1, 0, 0]     True
     [0, 0, 1]     True
     [1, 0, 1]    False
    badc
      elements  reduced
     [1, 3, 0]     True
     [0, 3, 1]     True
     [1, 3, 1]    False
    <BLANKLINE>
    """
    if n == None:
        n = identify_n(word)

    all_subwords = subword_element_association(word, n)
    db_name = obtain_db_name()
    with sqlite3.connect(db_name) as conn:
        cur = conn.cursor()
        cur.execute("""
        SELECT element
        FROM Lengths
        WHERE n_value = ?
        """,(n,))
        elements = [i[0] for i in cur.fetchall()]
    if filename == None:
        report = "In {}:\n\n".format(word)
    else:
        with open(filename, "w") as f:
            write = writer(f)
            write.writerow(["In {}:".format(word)])
            write.writerow([""])
    for element in elements:
        element_subwords = process_element(all_subwords, element)
        if element_subwords.loc[:,"reduced"].all():
            pass
        else:
            if filename == None:
                report += element + "\n"
                report += element_subwords.to_string(index = False)
                report += "\n"
            else:
                with open(filename, "a") as f:
                    write = writer(f)
                    write.writerow([element])
                element_subwords.to_csv(filename,index=False,mode="a")
                with open(filename, "a") as f:
                    f.write("\n")
    if filename == None:
        return report
    else:
        return filename

if __name__ == "__main__":
    import doctest
    doctest.testmod()
