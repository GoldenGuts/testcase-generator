import React, { useState, useEffect } from "react";
import { Form, Button, OverlayTrigger, Tooltip, Row, Col } from "react-bootstrap";
import Cookies from "js-cookie";
import axios from "../axios";
import { useNavigate } from "react-router-dom";
import ClipLoader from "react-spinners/ClipLoader";
import Select, { StylesConfig } from "react-select";

interface Option {
  value: string;
  label: string;
}

interface FormData {
  component: Option | null;
  labels: Option[];
}

const XRayFields: React.FC = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState<FormData>({ component: null, labels: [] });
  const [options, setOptions] = useState<{ labels: Option[]; components: Option[] }>({ labels: [], components: [] });
  const [isLoading, setLoading] = useState(false);
  const xrayTestKeys: string[] = localStorage.getItem("xray_test_keys")?.split(",") ?? [];

  const fetchData = async (type: 'labels' | 'components') => {
    setLoading(true);
    try {
      const storageKey = `jira_${type}`;
      const projectId = type === 'components' && localStorage.getItem("jira_issue_id")?.split("-")[0];
      const response = await axios.get(`/get-jira-${type}`, {
        headers: { Authorization: `Bearer ${Cookies.get("jira")}` },
        params: projectId ? { project_id: projectId } : {},
      });
      const data = response.data[type] || [];
      const formattedOptions = data.map((item: string) => ({ value: item, label: item }));
      localStorage.setItem(storageKey, JSON.stringify(formattedOptions));
      setOptions(prev => ({ ...prev, [type]: formattedOptions }));
    } catch (error) {
      console.error(`Failed to fetch ${type}:`, error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    ['labels', 'components'].forEach((type) => {
      const storedData = localStorage.getItem(`jira_${type}`);
      if (storedData) {
        setOptions(prev => ({ ...prev, [type]: JSON.parse(storedData) }));
      } else {
        fetchData(type as 'labels' | 'components');
      }
    });
  }, []);

  const handleComponentChange = (selectedOption: any) => {
    setFormData({ ...formData, component: selectedOption as Option });
  }

  const handleLabelsChange = (selectedOptions: any) => {
    setFormData({ ...formData, labels: selectedOptions as Option[] });
  }

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!formData.component && formData.labels.length === 0) {
      alert("At least one of Component or Labels is required!");
      return;
    }

    setLoading(true);

    const data = {
      component: formData.component ? formData.component.value : undefined, 
      labels: formData.labels.map(label => label.value),
    };
    
    const promises = xrayTestKeys.map((key) => {
      return axios.post(`/add_fields?key=${key}`, data, {
        headers: { Authorization: `Bearer ${Cookies.get("jira")}` }
      });
    });
  
    try {
      const responses = await Promise.all(promises);
      responses.forEach((response) => {
        console.log("Added successfully:", response.data);
      });
      navigate("/success");
    } catch (error: any) {
      console.error("Operation failed:", error);
      alert("Failed to add fields: " + (error.response ? error.response.data.error : error.message));
    } finally {
      setLoading(false);
    }
  };
  

  const selectStyles: StylesConfig<Option, true> = {
    control: styles => ({ ...styles, backgroundColor: "white" }),
    option: (styles, { isFocused, isSelected }) => ({
      ...styles, backgroundColor: isFocused ? "lightgray" : isSelected ? "gray" : undefined, color: "black"
    }),
  };

  const filterOption = (option: Option, inputValue: string) => {
    return (
      inputValue.length >= 3 &&
      option.label.toLowerCase().includes(inputValue.toLowerCase())
    );
  };

  const noOptionsMessage = ({ inputValue }: { inputValue: string }) => {
    return inputValue.length < 3
      ? "Type 3 letters to show suggestions"
      : "No options";
  };


  return (
    <div>
      <h3>Successfully created test cases in Jira {isLoading && <ClipLoader color="#36d7b7" />}</h3>
      <ul>
        {xrayTestKeys.map((key, index) => (
          <li key={index}>{key}</li>
        ))}
      </ul>
      <Form onSubmit={handleSubmit}>
        <Form.Label className="mt-3">Choose a component...</Form.Label>
        <Form.Group className="mb-3">
          <Select
            name="components"
            options={options.components}
            className="basic-single"
            classNamePrefix="select"
            value={formData.component}
            onChange={handleComponentChange}
            placeholder="Select one component"
            styles={selectStyles}
          />
        </Form.Group>
        <Form.Label>Choose labels...</Form.Label>
        <Form.Group className="mb-3">
          <Select
            isMulti
            name="labels"
            options={options.labels}
            className="basic-multi-select"
            classNamePrefix="select"
            value={formData.labels}
            onChange={handleLabelsChange}
            placeholder="Select multiple labels"
            styles={selectStyles}
            filterOption={filterOption}
            noOptionsMessage={noOptionsMessage}
          />
        </Form.Group>
        <div style={{ display: 'flex', flexDirection: 'column', gap:"10px", justifyContent: 'space-between', flexWrap: 'wrap' }}>
        <Button className="btn-custom" type="submit" disabled={isLoading}>Add to Ticket</Button>
        <OverlayTrigger
          placement="top"
          overlay={<Tooltip id="button-tooltip">Fetch latest labels if outdated. ~2 Minutes</Tooltip>}
        >
          <Button onClick={() => fetchData('labels')} disabled={isLoading}>Fetch Labels</Button>
        </OverlayTrigger>
        <Button onClick={() => fetchData('components')} disabled={isLoading}>Fetch Components</Button>
        </div>
      </Form>
    </div>
  );
};

export default XRayFields;
