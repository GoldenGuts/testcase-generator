import React, { useState, useEffect } from 'react';
import { Button, Form, Tab, Tabs, Row, Col } from 'react-bootstrap';
import axios from '../axios';
import Cookies from 'js-cookie';
import ClipLoader from 'react-spinners/ClipLoader';
import { useNavigate } from 'react-router-dom';
import {marked} from 'marked';

interface WorkflowProps {}

const Workflow: React.FC<WorkflowProps> = () => {
    const navigate = useNavigate();
    const [isLoading, setLoading] = useState<boolean>(false);
    const [workflow, setWorkflow] = useState<string>('');
    const [key, setKey] = useState<string>('edit');

    useEffect(() => {
        const savedWorkflow = localStorage.getItem('workflow');
        if (savedWorkflow) {
            setWorkflow(savedWorkflow);
        }
    }, []);

    const jiraIssueId = localStorage.getItem('jira_issue_id');

    const handleConfirm = async () => {
        setLoading(true);
        try {
            const response = await axios.post(
                '/update_jira_workflow',
                {
                    'jira_issue_id': jiraIssueId,
                    'workflow': workflow,
                },
                { headers: { Authorization: `Bearer ${Cookies.get('jira')}` } }
            );
            console.log('Jira workflow updated successfully:', response.data);
            alert('Workflow updated successfully!');
            navigate('/home');
        } catch (error: any) {
            console.error('Failed to update Jira workflow:', error);
            alert('Failed to update Jira workflow! ' + error.message);
        } finally {
            setLoading(false);
        }
    };

    const handleTextareaChange = (event: React.ChangeEvent<HTMLTextAreaElement>) => {
        const updatedWorkflow = event.target.value;
        setWorkflow(updatedWorkflow);
        localStorage.setItem('workflow', updatedWorkflow);
    };

    const getMarkdownText = () => {
        const rawMarkup = marked(workflow);
        return { __html: rawMarkup };
    };

    return (
        <div style={{ width: '100%' }}>
            <h4>
                Workflow for {jiraIssueId} {isLoading && <ClipLoader color="#36d7b7" size={20} />}
            </h4>
            <Tabs
                id="controlled-tab-example"
                activeKey={key}
                onSelect={(k) => setKey(k || 'edit')}
                className="mb-3"
            >
                <Tab eventKey="edit" title="Edit">
                    <Form.Control
                        as="textarea"
                        rows={15}
                        value={workflow}
                        onChange={handleTextareaChange}
                        disabled={isLoading}
                    />
                </Tab>
                <Tab eventKey="preview" title="Preview">
                    <div
                        dangerouslySetInnerHTML={getMarkdownText() as { __html: string}}
                        style={{ border: '1px solid #ccc', padding: '10px', borderRadius: '5px', minHeight: '300px' }}
                    />
                </Tab>
            </Tabs>
            <Button
                onClick={handleConfirm}
                disabled={isLoading}
                className="mt-3 btn-custom"
            >
                Confirm
            </Button>
        </div>
    );
};

export default Workflow;
