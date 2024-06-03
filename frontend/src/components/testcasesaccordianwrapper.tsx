import React from 'react';
import TestCasesAccordion from './testcasesaccordian'; 

const TestCasesAccordionWrapper: React.FC = () => {
  const storedTestCases = localStorage.getItem("testcases");
  let parsedJSON;

  // Check if 'testcases' is not null and is a valid JSON string
  if (storedTestCases) {
    try {
      parsedJSON = JSON.parse(storedTestCases);
    } catch (error) {
      console.error("Parsing error:", error);
      parsedJSON = []; // Default to an empty array in case of error
      alert("Error: Invalid test cases data found in local storage. Please try again.");
    }
  }

  // Ensure that parsedJSON is an array before passing it to TestCasesAccordion
  if (!Array.isArray(parsedJSON)) {
    console.error("Expected an array of test cases, but got:", typeof parsedJSON);
    parsedJSON = []; // Default to an empty array if it's not an array
  }

  return (
      <TestCasesAccordion testCases={parsedJSON || []} />
  );
};

export default TestCasesAccordionWrapper;
