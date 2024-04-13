import React, { useState, useEffect } from 'react';
import { Accordion, Card, Table } from 'react-bootstrap';

interface Step {
  action: string;
  data?: string;
  result: string;
}

interface TestCase {
  summary: string;
  steps: Step[];
}

interface TestCasesAccordionProps {
  testCases: TestCase[];
}

const TestCasesAccordion: React.FC<TestCasesAccordionProps> = ({ testCases }) => {
  const [activeKey, setActiveKey] = useState<string | null>(null);

  useEffect(() => {
    const content = document.querySelector('.main-content');
    if (content) {
      if (activeKey) {
        content.style.backgroundColor = 'white';  // Set background to white when any accordion item is active
      } else {
        content.style.backgroundColor = '';  // Reset background when all accordion items are collapsed
      }
    }
  }, [activeKey]);  // Effect runs on change of activeKey

  return (
    <Accordion defaultActiveKey="0" activeKey={activeKey} onSelect={(newKey) => setActiveKey(newKey === activeKey ? null : newKey)}>
      {testCases.map((testCase, index) => (
        <Card key={index}>
          <Accordion.Item eventKey={`${index}`}>
            <Accordion.Header>
              {testCase.summary}
            </Accordion.Header>
            <Accordion.Body>
              <Table striped bordered hover>
                <thead>
                  <tr>
                    <th>#</th>
                    <th>Action</th>
                    <th>Data</th>
                    <th>Result</th>
                  </tr>
                </thead>
                <tbody>
                  {testCase.steps.map((step, stepIndex) => (
                    <tr key={stepIndex}>
                      <td>{stepIndex + 1}</td>
                      <td>{step.action}</td>
                      <td>{step.data || 'N/A'}</td>
                      <td>{step.result}</td>
                    </tr>
                  ))}
                </tbody>
              </Table>
            </Accordion.Body>
          </Accordion.Item>
        </Card>
      ))}
    </Accordion>
  );
};

export default TestCasesAccordion;
