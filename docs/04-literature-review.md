# Literature review

Goal: ground each formal model used in ResumeLens in the literature, so the design
decisions (alphabet, abstraction level, automaton type, grammar structure) are
justified and not ad hoc.

## 1. Language classes and regular expressions
Chomsky (1956) classifies languages by the power of the grammars that generate
them; regular and context-free languages are the two levels ResumeLens uses.
Kleene (1956) proved that regular expressions and finite automata describe the
same languages. This is why extraction (regular expressions) and recognition
(finite automata) can be designed separately and still compose.
*Decision:* extraction only detects candidate strings with `re`; it never decides
equivalence or acceptance, which belong to the other models.

## 2. Finite-state transducers
Mohri (1997) presents finite-state transducers as the standard tool to map
strings to strings in language processing, and Roche & Schabes (1997) collect
applications such as morphology and text normalization. A transducer is exactly
the right model for "JS, Javascript -> JAVASCRIPT": the input alphabet are
characters, the output alphabet are canonical names.
*Decision:* the normalization transducers work on characters. A first transducer
removes case and separators, and a lexicon transducer (a trie over the alias
table) emits the canonical name when it reads the end marker. The 7-tuple has real
structure and each diagram stays readable.

## 3. Finite automata for pattern recognition
Hopcroft, Motwani & Ullman (2006) give the definitions of DFA, NFA and epsilon-NFA
and their equivalence, which is what we need to justify the type of each profile
automaton.
*Decision:* a profile is an ordered sequence of categories; each category accepts
one or more canonical qualifications. Profiles without optional categories are
DFAs (ML Engineer, Data Engineer). Profiles with an optional category use an
epsilon transition to skip it, so they are epsilon-NFAs (Full Stack, DevOps).
Sorting the input in the canonical order of the profile, between normalization
and recognition, makes the result independent of the order of the skills in the
resume.

## 4. Domain-specific languages and context-free grammars
Fowler (2010) describes when a DSL is worthwhile: a restricted notation for one
domain, with clear syntax and validation. EBNF (ISO/IEC 14977) is the standard
notation to write the grammar. textX (Dejanovic et al., 2017) builds a parser and
a metamodel from a grammar written in a EBNF-like notation, and reports syntax
errors with line and column.
*Decision:* the candidate profile is a DSL (contact, experience, education,
skills, classification). The grammar fixes the lexical rules (canonical names in
upper case) and the validator adds semantic checks (known qualifications and
profiles), so invalid profiles are rejected before rendering.

## 5. Tools
Romero (2021) presents pyformlang, the Python library used for transducers and
automata, as a library meant to learn and experiment with formal languages.
In pyformlang 1.0.11, which is the version used here, we checked that its FST is
nondeterministic, works on arbitrary symbols and has no composition operation;
the two normalization levels are therefore run one after the other.

## 6. Position of this work
Résumé parsers commonly rely on statistical or machine-learning extraction. ResumeLens
takes a deliberately different, fully formal approach: every step is a model with
a definition that can be written down and checked, and the system only reports
whether explicit qualifications satisfy a pattern. It does not rank candidates or
make hiring decisions.

## References
- Chomsky, N. (1956). Three models for the description of language. *IRE Transactions on Information Theory*, 2(3), 113-124.
- Dejanovic, I., Vaderna, R., Milosavljevic, G., & Vukovic, Z. (2017). TextX: A Python tool for domain-specific languages implementation. *Knowledge-Based Systems*, 115, 1-4.
- Fowler, M. (2010). *Domain-Specific Languages*. Addison-Wesley.
- Hopcroft, J. E., Motwani, R., & Ullman, J. D. (2006). *Introduction to Automata Theory, Languages, and Computation* (3rd ed.). Pearson.
- ISO/IEC 14977:1996. Information technology - Syntactic metalanguage - Extended BNF.
- Kleene, S. C. (1956). Representation of events in nerve nets and finite automata. In C. E. Shannon & J. McCarthy (Eds.), *Automata Studies* (Annals of Mathematics Studies, No. 34, pp. 3-42). Princeton University Press.
- Mohri, M. (1997). Finite-state transducers in language and speech processing. *Computational Linguistics*, 23(2), 269-311.
- Roche, E., & Schabes, Y. (Eds.). (1997). *Finite-State Language Processing*. MIT Press.
- Romero, J. (2021). Pyformlang: An educational library for formal language manipulation. *Proceedings of the 52nd ACM Technical Symposium on Computer Science Education (SIGCSE '21)*, 576-582.
