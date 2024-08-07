import React, { useEffect, useState } from "react";
import { Button, Col, Container, Form, Row, Alert } from "react-bootstrap";
import axios from "../axios";
import { XrayForm } from "./xrayForm";
import Cookies from "js-cookie";
import { isAxiosError } from "axios";
import "./settings.css";

interface SettingsProps {}

const Settings: React.FC<SettingsProps> = () => {
  interface JiraFormData {
    jira_email: string;
    jira_token: string;
  }
  interface VectorizationData {
    vectorization_api_key: string;
  }

  const [vectorizationData, setVectorizationData] = useState<VectorizationData>(
    {
      vectorization_api_key: "",
    }
  );

  const [jiraFormData, setJiraFormData] = useState<JiraFormData>({
    jira_email: "",
    jira_token: "",
  });
  const [cookiePresent, setCookiePresent] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [displayName, setDisplayName] = useState("");
  const [lastUpdated, setLastUpdated] = useState<string | null>(null);
  const [isLoginDisabled, setIsLoginDisabled] = useState(false);
  const [isSubmitAPIDisabled, setIsSubmitAPIDisabled] = useState(false);

  useEffect(() => {
    if (localStorage.getItem("jira_user") !== null) {
      setDisplayName(localStorage.getItem("jira_user") as string);
    }
    const lastUpdateTime = localStorage.getItem(
      "vectorization_api_key_last_updated"
    );
    if (lastUpdateTime) {
      setLastUpdated(lastUpdateTime);
    }
    const fetchVectorizationKey = async () => {
      try {
        const response = await axios.get("/get-vectorization-key");
        if (response.status === 200 && typeof response.data === "string") {
          setIsSubmitAPIDisabled(true);
        }
      } catch (error: any) {
        if (error.response && error.response.status === 403) {
          console.log("Vectorization API key has expired");
        } else {
          console.error("Error fetching vectorization key", error);
        }
      }
    };
    fetchVectorizationKey();
  }, []);

  useEffect(() => {
    const cookieValue = Cookies.get("jira");
    setCookiePresent(cookieValue !== undefined);
  }, [cookiePresent]);

  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = event.target;
    setJiraFormData({ ...jiraFormData, [name]: value });
  };

  const handleVectorizationAPIKeySubmission = async (
    event: React.FormEvent<HTMLFormElement>
  ) => {
    event.preventDefault();
    try {
      console.log("Data Provided: " + vectorizationData);

      const updateTime = new Date().toISOString();
      setLastUpdated(updateTime);
      localStorage.setItem("vectorization_api_key_last_updated", updateTime);

      await axios.post("/store-vectorization-key", {
        vectorization_api_key: vectorizationData.vectorization_api_key,
      });
      setIsSubmitAPIDisabled(true);
      setVectorizationData({ vectorization_api_key: "" });
    } catch (error) {
      alert("An unknown error occurred");
    }
  };

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);

    try {
      console.log(jiraFormData);
      const response = await axios.post<any>(
        "/authenticate",
        jiraFormData // Send the entire formData object
      );
      // setResponse(response.data); // Update response state (optional)
      console.log("Success! Response:", response.data); // Log response for debugging
      Cookies.set("jira", response.data.jwt, { expires: 7 });
      localStorage.setItem("jira_user", response.data.user);
      setDisplayName(response.data.user);
      setCookiePresent(true);
    } catch (error) {
      if (isAxiosError(error) && error.response) {
        setError("Authentication failed, wrong creds");
        setCookiePresent(false);
      } else {
        setError("An unknown error occurred");
        setCookiePresent(false);
      }
    }
  };

  const getTimeDifferenceInMinutes = (time: string): number => {
    const now = new Date();
    const lastUpdatedTime = new Date(time);
    const differenceInMilliseconds = now.getTime() - lastUpdatedTime.getTime();
    return Math.floor(differenceInMilliseconds / (1000 * 60));
  };

  const openAuthWindow = () => {
    const authWindow = window.open(
      "https://gait-rag-services-poc.azurewebsites.net/api/v1/authenticate",
      "authWindow",
      "width=600,height=600"
    );

    setIsLoginDisabled(true);

    const authWindowInterval = setInterval(() => {
      if (authWindow?.closed) {
        clearInterval(authWindowInterval);
        setIsLoginDisabled(false);
      }
    }, 1000);
  };

  return (
    <div className="settings">
      <Container>
        <Row>
          <Col>
            <Form onSubmit={handleSubmit}>
              <h3 className="mb-4 form-heading">Jira Auth Data</h3>
              {cookiePresent ? (
                <h6 className="datapresent-text">
                  Authenticated as: {displayName}
                </h6>
              ) : (
                <></>
              )}
              {error && <Alert variant="danger">{error}</Alert>}

              <Form.Group
                className="mb-3"
                controlId="exampleForm.ControlInput1"
              >
                <Form.Control
                  type="text"
                  placeholder="JIRA Token"
                  name="jira_token"
                  value={jiraFormData.jira_token}
                  onChange={handleInputChange}
                />
              </Form.Group>
              <Form.Group
                className="mb-3"
                controlId="exampleForm.ControlInput1"
              >
                <Form.Control
                  type="email"
                  placeholder="JIRA Email"
                  name="jira_email"
                  value={jiraFormData.jira_email}
                  onChange={handleInputChange}
                />
              </Form.Group>

              <Button className="ml-5 btn-custom" type="submit">
                Authenticate
              </Button>
            </Form>
          </Col>
          <Col>
            <XrayForm></XrayForm>
          </Col>
        </Row>
        {process.env.REACT_APP_ENABLE_VECTOR_API === "true" && (
          <Row className="pt-5">
            {!isSubmitAPIDisabled && (
              <div
                style={{
                  color: "red",
                  textAlign: "center",
                  marginTop: "20px",
                }}
              >
                Warning: Vectorization API key is not present.
              </div>
            )}
            <Col>
              <Form onSubmit={handleVectorizationAPIKeySubmission}>
                <h3 className="mb-4 form-heading">
                  Vectorization API Key - Expires in 1hr
                </h3>
                {lastUpdated && (
                  <h6 className="last-updated">
                    Last updated: {getTimeDifferenceInMinutes(lastUpdated)}{" "}
                    minutes ago
                  </h6>
                )}

                <Form.Group className="mb-3" controlId="vectorizationApiKey">
                  <Form.Control
                    type="text"
                    placeholder="Enter your API Key"
                    name="vectorization_api_key"
                    value={vectorizationData.vectorization_api_key}
                    onChange={(e) =>
                      setVectorizationData({
                        vectorization_api_key: e.target.value,
                      })
                    }
                  />
                </Form.Group>

                <Container className="d-flex justify-content-center align-items-center">
                  <Row>
                    <Col className="">
                      <Button
                        className="btn-custom"
                        onClick={openAuthWindow}
                        disabled={isLoginDisabled}
                      >
                        Get API Key
                      </Button>
                    </Col>
                    <Col className="">
                      <Button
                        className="btn-custom"
                        type="submit"
                        disabled={isSubmitAPIDisabled}
                      >
                        Submit API Key
                      </Button>
                    </Col>
                    <Col className="">
                      <Button
                        className="btn-custom"
                        onClick={() => {
                          axios.delete("/clear-vectorization-key");
                          setIsSubmitAPIDisabled(false);
                        }}
                      >
                        Reset API Key
                      </Button>
                    </Col>
                  </Row>
                </Container>
              </Form>
            </Col>
          </Row>
        )}
      </Container>
    </div>
  );
};

export default Settings;
