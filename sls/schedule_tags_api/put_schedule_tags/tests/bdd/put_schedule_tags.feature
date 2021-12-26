@integration_test
@ABGN-8151-api-rds-ec2-scheduling
Feature: Add, Update schedule tags to RDS/EC2 instance

 Scenario Outline: Positive scenario 1 - Create the schedule tag on an Instance
    Given PUT Schedule API exists
    And valid oauth2 token for API authorization generated
    And VPCx account is valid
    And Region is valid
    And Resource type is set to <res_type>
    And <res_type> instance exists
    And instance <status_tags> schedule tags
    When we invoke the api
    Then API returns a status of 200
    And Valid schedule tag present for <res_type> instance
    Examples: Success for <res_type> instance that <status_tags> schedule tags
       | res_type    | status_tags   |
       | ec2         | has           |
       | ec2         | does not have |
       | rds         | has           |
       | rds         | does not have |

 Scenario: Negative Scenario 1 - Invalid authorization token provided
   Given PUT Schedule API exists
   And invalid oauth2 token for API authorization generated
   When we invoke the api
   Then API returns a status of 401

 Scenario: Negative Scenario 2 - Invalid account ID provided
   Given PUT Schedule API exists
   And valid oauth2 token for API authorization generated
   And VPCx account is not valid
   When we invoke the api
   Then API returns a status of 400

 Scenario: Negative Scenario 3 - Invalid region provided
   Given PUT Schedule API exists
   And valid oauth2 token for API authorization generated
   And VPCx account is valid
   And Region is not valid
   When we invoke the api
   Then API returns a status of 400

  Scenario: Negative Scenario 3 - Invalid resource type provided
   Given PUT Schedule API exists
   And valid oauth2 token for API authorization generated
   And VPCx account is valid
   And Region is valid
   And Resource type is not valid
   When we invoke the api
   Then API returns a status of 400

  Scenario Outline: Negative Scenario 4 - Invalid resource provided
   Given PUT Schedule API exists
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

 Scenario: Negative scenario 5 - Create the schedule tag using Cluster-ID
  Given PUT Schedule API exists
  And valid oauth2 token for API authorization generated
  And VPCx account is valid
  And Region is valid
  And Resource type is set to rds
  And Resource is a cluster
  When we invoke the api
  Then API returns a status of 400
  And error contains Cluster cannot be scheduled for start or stop

 Scenario Outline: Negative scenario 6 - Error creating the schedule tag with invalid tag
  Given PUT Schedule API exists
  And valid oauth2 token for API authorization generated
  And VPCx account is valid
  And Region is valid
  And Resource type is set to <res_type>
  And <res_type> instance exists
  When we invoke the api with invalid payload
  Then API returns a status of 400
  Examples: Error creating resource for <res_type> with invalid tag
       | res_type    |
       | ec2         |
       | rds         |
