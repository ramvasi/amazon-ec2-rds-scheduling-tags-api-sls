@integration_test
@ABGN-8151-api-rds-ec2-scheduling
Feature: Retrieve schedule tags from RDS instance

 Scenario Outline: Positive scenario 1 - Get schedule tags
    Given GET Schedule API exists
    And valid oauth2 token for API authorization generated
    And VPCx account is valid
    And Region is valid
    And Resource type is set to <res_type>
    And <res_type> instance exists
    And instance <status_tags> schedule tags
    When we invoke the api
    Then API returns a status of 200
    And response contains <message>
    Examples: Success for <res_type> instance that <status_tags> schedule tags
       | res_type    | status_tags   | message            |
       | ec2         | has           | list with tag keys |
       | ec2         | does not have | empty list         |
       | rds         | has           | list with tag keys |
       | rds         | does not have | empty list         |

 Scenario: Negative Scenario 1 - Invalid authorization token provided
   Given GET Schedule API exists
   And invalid oauth2 token for API authorization generated
   When we invoke the api
   Then API returns a status of 401

 Scenario: Negative Scenario 2 - Invalid account ID provided
   Given GET Schedule API exists
   And valid oauth2 token for API authorization generated
   And VPCx account is not valid
   When we invoke the api
   Then API returns a status of 400

 Scenario: Negative Scenario 3 - Invalid region provided
   Given GET Schedule API exists
   And valid oauth2 token for API authorization generated
   And VPCx account is valid
   And Region is not valid
   When we invoke the api
   Then API returns a status of 400

  Scenario: Negative Scenario 3 - Invalid resource type provided
   Given GET Schedule API exists
   And valid oauth2 token for API authorization generated
   And VPCx account is valid
   And Region is valid
   And Resource type is not valid
   When we invoke the api
   Then API returns a status of 400

  Scenario Outline: Negative Scenario 4 - Invalid resource provided
   Given GET Schedule API exists
   And valid oauth2 token for API authorization generated
   And VPCx account is valid
   And Region is valid
   And Resource type is set to <res_type>
   And <res_type> Resource does not exist
   When we invoke the api
   Then API returns a status of 404
   Examples: <res_type> Resource does not exist
       | res_type    |
       | ec2         |
       | rds         |