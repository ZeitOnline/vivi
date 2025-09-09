Feature: Login

  Scenario: Login and redirect to main page
     Given we are on the homepage
      When we have valid credentials
      And we log in
      Then we see the authenticated homepage
      And we see our login name and logout button
