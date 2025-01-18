## How to use this app

Using the tabs above you can either upload a CSV of Gherkin scenarios, or paste them in.

### Upload a Testmo CSV
If you have Gherkin scenarios stored in the description fields of your Testmo test cases, then Testmo allows for easy bulk exporting of these cases to a CSV.

Export the description field, and optionally the test case name, and those will be handled by the formatter. Other Testmo fields included in the export will be ignored.

For best results your Gherkin code needs to be formatted consistently. The number of spaces used to indent shouldn't matter (nor should blank lines), but key words (Feature, Scenario, Given, etc) need to be properly capitalised i.e. only the first character.

The below example shows everything that is supported by this converter:

```gherkin
Feature: The name of your feature

Background:
  Given some setup
  And some more setup
  
Scenario: The scenario to be tested
  Given this first step
  And this other step
  When I do this thing
  But not this thing
  Then I can expect to see this
```

If there are other lines in your description then these will likely come out unformatted, but you may see unexpected results.

#### Formatting options

There are two formatting options:

#### Testmo Case Name

This option will create a hierarchy based on the Testmo case name. 

It will not attempt to organise your cases, but merely write them out in the order presented in the CSV.

**_This option requires the Testmo Case Name to be present in the CSV_**

#### Gherkin Feature Name

This option will create a hierarchy based on the Gherkin Feature name.

It will attempt to group scenarios together where they share a feature name. It will also only write out the background once per feature name.

This will only work if your feature naming is consistent.

**_This option will ignore the Testmo Case Name (if present) in the CSV_**

### Paste Gherkin code

A basic converter is provided for times when you need to quickly convert a scenario or two.

The same Gherkin formatting as above is expected. Simply paste it in and hit `Ctrl/Cmd + Enter`