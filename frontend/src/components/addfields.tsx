import React, { useState, useEffect } from "react";
import { Form, Button, OverlayTrigger, Tooltip } from "react-bootstrap";
import Cookies from "js-cookie";
import axios from "../axios";
import { useNavigate } from "react-router-dom";
import ClipLoader from "react-spinners/ClipLoader";
import Select, { StylesConfig } from "react-select";

interface FormData {
  component: string;
  label: Array<{ value: string; label: string }>;
}

interface LabelOption {
  value: string;
  label: string;
}

const XRayFields: React.FC = () => {
  const renderTooltip = () => (
    <Tooltip id="button-tooltip" className="danger-tooltip">
      Don't do it if you see the labels and have not updated the labels recently
      in your Jira.
    </Tooltip>
  );

  const navigate = useNavigate();
  const xrayTestKeys: string[] =
    localStorage.getItem("xray_test_keys")?.split(",") ?? [];

  const [formData, setFormData] = useState<FormData>({
    component: "",
    label: [],
  });
  const [labelOptions, setLabelOptions] = useState<LabelOption[]>([]);
  const [isLoading, setLoading] = useState(false);

  const fetchLabels = async () => {
    try {
      setLoading(true);
      const response = await axios.get("/get-jira-labels", {
        headers: { Authorization: `Bearer ${Cookies.get("jira")}` },
      });
      const labelsArray = response.data.labels || [];
      const formattedOptions = labelsArray.map((label: string) => ({
        value: label,
        label,
      }));
      localStorage.setItem("jira_labels", JSON.stringify(formattedOptions));
      window.location.reload();
    } catch (error) {
      console.error("Failed to fetch labels:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const labels = localStorage.getItem("jira_labels");
    setLabelOptions(labels ? JSON.parse(labels) : []);
  }, []);

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    if (!formData.component || formData.label.length === 0) {
      alert("Component and Label are required!");
      return;
    }
    event.preventDefault();
    if (!Cookies.get("jira")) {
      console.error("Jira Data is not present!");
      return;
    }

    setLoading(true);

    const promises = xrayTestKeys.map((key) => {
      return axios.post(
        "/add_fields",
        {
          key,
          label: formData.label.map((l) => l.value),
          component: formData.component,
        },
        { headers: { Authorization: `Bearer ${Cookies.get("jira")}` } }
      );
    });

    try {
      const responses = await Promise.all(promises);
      responses.forEach((response) => {
        console.log("Added successfully:", response.data);
      });
      navigate("/success");
    } catch (error: any) {
      if (error.response) {
        if (error.response.status === 403) {
          alert("You do not have permission to perform this action.");
        } else if (error.response.status === 500) {
          alert("Server error occurred. " + JSON.stringify(error.response.data));
        } else {
          alert("Operation failed: " + error.response.data.error);
        }
      } else {
        alert("Operation failed: " + error.message);
      }
      console.error("Operation failed:", error);
    } finally {
      setFormData({ component: "", label: [] });
      setLoading(false);
    }
  };

  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = event.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleLabelChange = (selectedOptions: any) => {
    setFormData({ ...formData, label: selectedOptions || [] });
  };

  const selectStyles: StylesConfig<LabelOption, true> = {
    control: (styles) => ({ ...styles, backgroundColor: "white" }),
    option: (styles, { isFocused, isSelected }) => {
      return {
        ...styles,
        backgroundColor: isFocused
          ? "lightgray"
          : isSelected
          ? "gray"
          : undefined,
        color: "black",
      };
    },
  };

  const filterOption = (option: LabelOption, inputValue: string) => {
    return inputValue.length >= 3 && option.label.toLowerCase().includes(inputValue.toLowerCase());
  };

  const noOptionsMessage = ({ inputValue }: { inputValue: string }) => {
    return inputValue.length < 3 ? "Type 3 letters to show suggestions" : "No options";
  };

  return (
    <div>
      <h3>
        Successfully created test cases in Jira{" "}
        {isLoading ? <ClipLoader color="#36d7b7" /> : null}
      </h3>
      <ul>
        {xrayTestKeys.map((key, index) => (
          <li key={index}>{key}</li>
        ))}
      </ul>
      <div>
        Add your component and label (only existing component will work)
      </div>

      <Form onSubmit={handleSubmit}>
        <Form.Group className="mb-3">
          <Form.Control
            type="text"
            placeholder="Component"
            name="component"
            value={formData.component}
            onChange={handleInputChange}
          />
        </Form.Group>
        <Form.Group className="mb-3">
          <Select
            isMulti
            name="labels"
            options={labelOptions}
            className="basic-multi-select"
            classNamePrefix="select"
            value={formData.label}
            onChange={handleLabelChange}
            styles={selectStyles}
            filterOption={filterOption}
            noOptionsMessage={noOptionsMessage}
          />
        </Form.Group>

        <Button className="ml-5 btn-custom" type="submit" disabled={isLoading}>
          Add to Ticket
        </Button>
        <OverlayTrigger
          placement="top"
          delay={{ show: 250, hide: 400 }}
          overlay={renderTooltip}
        >
          <Button
            style={{ marginLeft: "10%" }}
            className="ml-5 btn-custom"
            onClick={fetchLabels}
            disabled={isLoading}
          >
            Fetch Labels (~2 mins)
          </Button>
        </OverlayTrigger>
      </Form>
    </div>
  );
};

export default XRayFields;
