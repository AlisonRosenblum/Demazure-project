#!/usr/bin/env python3

import sqlite3
from string import ascii_lowercase
from os import path

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

def str_join(separated):
    """
    joins a list of strings into a single string

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
    >>> str_join(['a','b','c','d'])
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
    return str_join(element)

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

    #create table in database
    # path_name = __file__[:__file__.find("Demazure.py")-1]
    # rel_path_name = path.relpath(path_name)
    # db_name = path.join(rel_path_name,"S_n.sqlite")
    db_name = "S_n.sqlite"
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

if __name__ == "__main__":
    import doctest
    doctest.testmod()
