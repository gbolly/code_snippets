import React, { useContext, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faEye, faEyeSlash } from '@fortawesome/free-solid-svg-icons'
import {
  Button,
  Col,
  Container,
  Form,
  InputGroup,
  Row,
  Spinner
} from 'react-bootstrap';

import AuthContext from '../../Context/authContext';
import { userLogin } from '../../Services/api';
import { saveToStore } from '../../Utils/storage-helpers';
import Notification, { useNotification } from 'src/Components/Notification';
import './style.scss';


const LoginPage = () => {
  const [userEmail, setUserEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [passwordShown, setPasswordShown] = useState(false);
  const { setAuth } = useContext(AuthContext);
  let navigate = useNavigate();
  const { notifyError, onClose, notification } = useNotification();

  const validateForm = () => {
    return userEmail.length > 0 && password.length > 0;
  };

  const togglePassword = () => {
    setPasswordShown(!passwordShown);
  };

  const handleSubmit = async (e) => {
    setIsLoading(true);
    e.preventDefault();
    const email = userEmail.toLowerCase();
    const data = {
      email,
      password,
    };
    const login_res = await userLogin(data);
    setIsLoading(false);
    if (login_res.status !== 200) {
      const errMsg = login_res.response.data.detail;
      notifyError({ message: errMsg })
      setAuth(false);
    } else {
      await saveToStore('accessToken', login_res.data.access_token);
      await saveToStore('user', login_res.data.user);
      setAuth(true);
    }
  };

  return (
    <>
      <Container className='sharedAuthStyles signinContainer'>
        <Notification id="login-error" onClose={onClose} {...notification} />
        <div className='header mb-5'>
          <h4 className='text-secondary'>Welcome back</h4>
          <p className='text-muted'>
            Enter your credentials to access your account
          </p>
        </div>
        <Form onSubmit={handleSubmit}>
          <Row className='mb-5'>
            <Col>
              <Form.Group controlId='formEmail'>
                <Form.Control
                  autoFocus
                  className='formInput text-dark'
                  type='text'
                  placeholder='Email'
                  value={userEmail}
                  onChange={(e) => setUserEmail(e.target.value)}
                />
              </Form.Group>
            </Col>
          </Row>
          <Row className='mb-5'>
            <Col>
              <Form.Group controlId='formPassword'>
                <InputGroup>
                  <Form.Control
                    className='formInput text-dark'
                    placeholder='Password'
                    type={passwordShown ? 'text' : 'password'}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                  />
                  <InputGroup.Text>
                    <FontAwesomeIcon
                      icon={passwordShown ? faEye : faEyeSlash}
                      onClick={togglePassword}
                    />
                  </InputGroup.Text>
                </InputGroup>
                <Form.Text className="float-end">
                  Forgot your password?
                  <Button
                    variant="link"
                    className="resetPasswordLink"
                    onClick={() => navigate("/reset-password")}
                  >
                    Reset Password
                  </Button>
                </Form.Text>
              </Form.Group>
            </Col>
          </Row>
          <div className='text-center'>
            <Button
              className='business submitButton'
              type='submit'
              disabled={!validateForm() || isLoading}
            >
              {isLoading && (
                <Spinner
                  as="span"
                  animation="border"
                  size="sm"
                  role="status"
                  aria-hidden="true"
                />
              )}
              Sign in
            </Button>
          </div>
        </Form>
        <div>
          <p className='text-center text-secondary mt-3'>
            Don't have an account?
            <span>
              <Button
                variant='link'
                className='px-1 signinLink'
                onClick={() => navigate('/signup')}
              >
                Register
              </Button>
            </span>
          </p>
        </div>
      </Container>
    </>
  )
};

export default LoginPage;
