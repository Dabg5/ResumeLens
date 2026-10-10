# Candidate DSL

The candidate DSL records extracted information and profile recognition results
in a small, readable language. It serializes one candidate and does not rank
candidates.

## EBNF

The notation below uses `{ X }` for zero or more repetitions, `[ X ]` for an
optional part, and quoted text for literal terminals. `STRING`, `INT`, and `ID`
are textX built-in lexical rules. The named regular expressions are terminals.

```ebnf
CandidateProfile = "candidate", STRING, "{",
                   [ Contact ], [ Experience ], [ Education ],
                   Skills, Classification, "}" ;

Contact          = "contact", "{",
                   [ "emails", ":", STRING, { ",", STRING } ],
                   [ "phones", ":", STRING, { ",", STRING } ],
                   [ "urls", ":", STRING, { ",", STRING } ], "}" ;
Experience       = "experience", "{",
                   [ "years", ":", INT ],
                   [ "periods", ":", STRING, { ",", STRING } ], "}" ;
Education        = "education", "{", { EducationEntry }, "}" ;
EducationEntry   = STRING, [ "at", STRING ] ;
Skills           = "skills", "{", { SkillGroup }, "}" ;
SkillGroup       = ID, ":", Canonical, { ",", Canonical } ;
Classification   = "classification", "{", { ProfileResult }, "}" ;
ProfileResult    = "profile", ProfileKey, ":", Verdict,
                   [ "sequence", "[", [ Canonical, { ",", Canonical } ], "]" ],
                   [ "missing", "[", [ STRING, { ",", STRING } ], "]" ] ;

Canonical        = /[A-Z][A-Z0-9_]*/ ;
ProfileKey       = /[a-z][a-z_]*/ ;
Verdict          = "ACCEPTED" | "REJECTED" ;
```

## Structure and repetition

A document has one candidate name, followed in order by optional contact,
experience, and education blocks, then required skills and classification
blocks. Each block is enclosed in braces. Contact fields and experience fields
are optional; a field may list multiple comma-separated strings. Education,
skill groups, and profile results may repeat. A skill group has one category
identifier and one or more canonical qualifications. A profile result has a
profile key and verdict, with optional canonical sequence and missing-category
list.

## Lexical and semantic rules

Strings use textX's quoted `STRING` syntax; the serializer escapes backslashes
and double quotes. Canonical qualification names contain uppercase ASCII
letters, digits, and underscores, beginning with a letter. Profile keys use
lowercase ASCII letters and underscores, beginning with a letter. Verdicts are
the literal words `ACCEPTED` or `REJECTED`.

Parsing checks token order, delimiters, and lexical forms. Semantic validation
also requires canonical names to exist in the alias table, profile keys to name
a defined profile, accepted results to include a sequence, and every sequence
symbol to belong to that profile's alphabet. Repeating a skill category is an
error. Syntax and lexical errors report their line and column.
