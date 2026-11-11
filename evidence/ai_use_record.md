AI Records

Tools Used: AI Coding Assistant

Summary of Use:
Through this assignment, I employed an AI helper as my programming partner. This was done utilizing the AI to figure out the complex code, prepare a list of automated tests to be carried out, examine potential problems with code, and make necessary changes in the source code. It was also utilized to find out if my engineering work was appropriate and rectify the unintended consequences of changes in the code (for example, test failures due to refactoring). The table below shows the main activities that took place and my assessment of the responses provided by the AI in Task 6.

Interaction 1: Adding CR-01 (Express Delivery)

My Input: "I need to integrate Express Delivery for CR-01 – it has a price of 1200 cents and is subject to no exceptions. How do I do that in the delivery logic that is already in use?"

AI Recommendation: The AI suggested adding the term express against the existing delivery condition whereby if fulfilled in delivery and express.

My Evaluation: I did not accept this recommendation as I knew that combining these terms would result in the incorrect waiver of express under the cr-01 condition from CR-01 condition #2. Instead, I asked AI to write a separate if fulfilled = express branch in delivery_fee(). I also confirmed this by writing a test_express_never_waived_above_standard_threshold which successfully passed after I made the corrections.

Interaction 2: Refactoring Strategy

My Prompt: The quote and place_order functions contain duplicated code. What is the best way to refactor this?

AI Recommendation: AI recommended to apply the Extract Method strategy to create an _price_request helper as well as to extract the delivery logic into a delivery_fee() function.

My Evaluation: I accepted this recommendation since it perfectly matched with the refactoring techniques I learned in class. I proved that the refactoring did not affect the existing behavior by running the tests both before and after refactoring; the same errors occurred demonstrating that nothing new has been introduced.

Interaction 3: Resolving the Issue with Student Discounts


My Prompt: “I got a failure in the test test_student_discount_exactly_at_threshold as the programmer employed the ‘greater than’ symbol instead of ‘greater than or equal'. Should that be corrected in the process of refactoring?"


AI Recommendation: The AI considered that it was a good idea to fix the problem on the fly by substituting "greater than" with "greater than or equal".


My Evaluation: I MODIFIED this recommendation. Despite the fact, I had found the correct solution, I understood that it is not allowed to make such a change at the refactoring stage as it does not comply with the idea of making changes without changing the functionality in any way. It meant that I decided to document the issue, retain the error in the process of resolving the task, and apply the solution in a separate bug-fixing commit later.