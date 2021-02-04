In every iteration, we evaluate each bug in terms
of the following criteria:

* Root Cause:
  What went wrong in the compiler?

* Symptom:
  What this bug causes? (e.g., reject correct code,
  accept incorrect code, crash, etc.)

* Affected language features:
  What kind of features this bug affects?

* Characteristics of test case:
  (What kind of language featue the test that triggers the bug involves?)


For example, by examining this bug (https://youtrack.jetbrains.com/issue/KT-22474)
we can say:

* Root cause: Wrong subtyping (between intersection type and Any.
* Symptom: Soundness bug)
* Affected language features: intersection types
* Characteristics of test case: Parameterized classes, parameterized functions
  variance, inheritance


Based on the following, we have to classify the bugs into different
categories. Note that we don't know these categories apriori.
