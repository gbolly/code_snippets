import React, { useState, useContext, useEffect, useCallback } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  Container,
  Row,
  Col,
  Form,
  Button,
  Alert,
  Modal,
} from "react-bootstrap";
import { useFlutterwave, closePaymentModal } from "flutterwave-react-v3";

import { clean_naira_format, clean_dollar_format } from "../../utils/utilities";
import AuthContext from "../../context/authContext";
import Header from "../../components/Header";
import OrderItem from "../../components/OrderItem";
import TermsAndConditions from "../../components/TermsAndConditions";
import Checkmark from "../../components/Checkmark";

import LoginPage from "../login";
import {
  getOrder,
  verifyPaymentTrans,
  sendCouponRequest,
} from "../../services/api";
import { ROUNDED_BUTTON } from "../../utils/styles/buttons";

import { Colors } from "../../utils/styles";
import styles from "./style";

export const orderStatusMapping = {
  1: "success",
  2: "fail",
  3: "pending",
};

const CheckOutPage = (props) => {
  const [order, setOrder] = useState(null);
  const [error, setError] = useState("");
  const [hasError, setHasError] = useState(false);
  const [message, setMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [discountCode, setDiscountCode] = useState("");
  const [acceptCondiiton, setAcceptConditions] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [modalShow, setModalShow] = React.useState(false);

  const handleClose = () => setShowModal(false);
  const handleShow = () => setShowModal(true);
  const handleModalClose = () => setModalShow(false);
  const handleModalShow = () => setModalShow(true);

  const { isAuthenticated } = useContext(AuthContext);
  const navigate = useNavigate();
  let params = useParams();

  const naira_config = {
    public_key: process.env.REACT_APP_FLUTTER_PUBKEY,
    tx_ref: `BES-${Date.now()}`,
    amount:
      order?.additional_payment > 0
        ? order?.additional_payment_naira
        : order?.order_total_naira,
    currency: "NGN",
    payment_options: "card,mobilemoney,ussd",
    customer: {
      email: order?.shopper.email,
      phonenumber: order?.shopper.phone_no,
      name: `${order?.shopper.first_name} ${order?.shopper.last_name}`,
    },
    customizations: {
      title: "beta-eshopping",
      description: `Payment for order: ${order?.order_id}`,
      logo: "https://st2.depositphotos.com/4403291/7418/v/450/depositphotos_74189661-stock-illustration-online-shop-log.jpg",
    },
  };

  const dollar_config = {
    public_key: process.env.REACT_APP_FLUTTER_PUBKEY,
    tx_ref: `BES-${Date.now()}`,
    amount:
      order?.additional_payment > 0
        ? order?.additional_payment
        : order?.order_total,
    currency: "USD",
    payment_options: "card,mobilemoney,ussd",
    customer: {
      email: order?.shopper.email,
      phonenumber: order?.shopper.phone_no,
      name: `${order?.shopper.first_name} ${order?.shopper.last_name}`,
    },
    customizations: {
      title: "beta-eshopping",
      description: `Payment for order: ${order?.order_id}`,
      logo: "https://st2.depositphotos.com/4403291/7418/v/450/depositphotos_74189661-stock-illustration-online-shop-log.jpg",
    },
  };

  const getOrderDetails = useCallback(async (id) => {
    const orderDetailsRes = await getOrder(id);

    if (orderDetailsRes.response?.status >= 400) {
      setError(orderDetailsRes.response.data.detail);
    } else {
      setOrder(orderDetailsRes.data);
    }
  }, []);

  const validateDiscountForm = () => {
    return discountCode.length > 0;
  };

  useEffect(() => {
    getOrderDetails(params.id);
  }, [params, getOrderDetails]);

  const validateForm = () => {
    return acceptCondiiton === true;
  };

  const handleFlutterPaymentNaira = useFlutterwave(naira_config);
  const handleFlutterPaymentDollar = useFlutterwave(dollar_config);

  const saveTransaction = async (transaction, orderId) => {
    const transactionData = {};
    transactionData.order = orderId;
    transactionData.transaction_id = transaction.transaction_id;

    const transactionStatus = await verifyPaymentTrans(transactionData);

    if (transactionStatus.status !== 200) {
      const err = transactionStatus.response.data;
      const errMsg = Object.keys(err).map((key) => {
        return `${[key]}: ${err[key]}`;
      });
      setError(errMsg);
    } else {
      const { status = "pending", order } = transactionStatus.data;
      navigate(
        `/payment?status=${orderStatusMapping[status]}&ref=${order.order_id}`
      );
    }
  };

  const handleSubmit = async (e) => {
    setIsLoading(true);
    e.preventDefault();
    const coupon_res = await sendCouponRequest({ discountCode });
    if (coupon_res.status !== 200) {
      const err = coupon_res.response.data;
      const errMsg = Object.keys(err).map((key) => {
        return `${err[key]}`;
      });
      setError(errMsg);
      setHasError(true);
    } else {
      setMessage(coupon_res.data.message);
      setHasError(false);
      setDiscountCode("");
      setTimeout(() => {
        setIsLoading(false);
        window.location.reload(false);
      }, 3000);
    }
  };

  if (!isAuthenticated) {
    return <LoginPage path="/pending-orders" />;
  }

  return (
    <>
      <Header hideAuth={true} isAuthenticated={isAuthenticated} />

      <section style={{ height: "100vh" }} className="container">
        <Modal
          {...props}
          size="md"
          backdrop="static"
          aria-labelledby="contained-modal-title-vcenter"
          centered
          show={modalShow}
          onHide={handleModalClose}
        >
          <Modal.Header closeButton>
            <Modal.Title id="contained-modal-title-vcenter">
              Bank Details - USD/NGN
            </Modal.Title>
          </Modal.Header>
          <Modal.Body>
            <h5>Bank: Guaranty Trust Bank Ltd</h5>
            <p>Address: 31 Mobolaji Bank Anthony Way, Ikeja, Lagos, Nigeria.</p>
            <p>Sort Code: 058-152023</p>
            <p>Swift Code: GTBINGLA</p>
            <p>NUBAN: 0679125931</p>
            <p>Account Name: Beta Courier Services Ltd</p>
            <p>DOLLAR Account No: 0679125931</p>
            <p>NAIRA Account No: 0002887073</p>
            <p>
              Kindly send proof of payment with order ID to
              info@beta-eshopping.com.
            </p>
          </Modal.Body>
          <Modal.Footer>
            <Button
              size="md"
              style={{
                ...ROUNDED_BUTTON,
                width: 100,
                height: 40,
                margin: "0 auto",
              }}
              onClick={handleModalClose}
            >
              OK
            </Button>
          </Modal.Footer>
        </Modal>

        {error && (
          <Alert
            variant="danger"
            style={{ width: "70%", margin: "0 auto", textAlign: "center" }}
            onClose={() => setError("")}
            dismissible
          >
            {error}
          </Alert>
        )}
        <Container style={{ height: "70%" }}>
          <Modal show={showModal} onHide={handleClose}>
            <Modal.Header closeButton>
              <Modal.Title>Terms and Conditions</Modal.Title>
            </Modal.Header>
            <Modal.Body>
              <TermsAndConditions />
            </Modal.Body>
            <Modal.Footer>
              <Button variant="secondary" onClick={handleClose}>
                Close
              </Button>
            </Modal.Footer>
          </Modal>
          {order?.additional_payment > 0 ? (
            <Row style={{ height: "100%" }}>
              <Col lg={6} style={{ marginTop: 70 }}>
                <h4 style={{ width: 460, fontWeight: 600 }}>Checkout</h4>
                <OrderItem order={!isLoading && order} />
              </Col>
              <Col lg={4} style={{ margin: "90px auto" }}>
                <Row className="mt-3">
                  <Col>
                    <p style={styles.checkoutLabels}>Additional Payment</p>
                  </Col>
                  <Col>
                    <p style={styles.checkoutValues}>
                      {clean_dollar_format(order?.additional_payment)}
                    </p>
                  </Col>
                </Row>
                <hr />
                <Row>
                  <Col>
                    <h5 style={styles.checkoutLabels}>Total</h5>
                  </Col>
                  <Col>
                    <h5 style={styles.checkoutValues}>
                      {clean_dollar_format(order?.additional_payment)}
                    </h5>
                  </Col>
                  <span
                    className="mt-2"
                    style={{ ...styles.checkoutValues, color: Colors.ALERT }}
                  >
                    Total amount in Naira:{" "}
                    {clean_naira_format(order?.additional_payment_naira)}
                  </span>
                </Row>
                <Row>
                  <Form.Group
                    className="mt-5 mb-3"
                    id="formGridCheckbox"
                    style={{ display: "inline-flex" }}
                  >
                    <Form.Check
                      type="checkbox"
                      label="I accept the "
                      onChange={(e) => {
                        setAcceptConditions(e.target.checked);
                      }}
                    />
                    <button
                      className="form-check-label"
                      style={styles.termsAndConditionButton}
                      onClick={handleShow}
                    >
                      terms and conditions
                    </button>
                  </Form.Group>
                  <Button
                    disabled={!validateForm()}
                    style={{
                      backgroundColor: Colors.BES_PURPLE,
                      height: 53,
                      width: 200,
                      margin: "0 auto",
                      border: "none",
                      marginBottom: 10
                    }}
                    onClick={(e) => {
                      handleFlutterPaymentNaira({
                        callback: (response) => {
                          saveTransaction(response, order?.id);
                          closePaymentModal();
                        },
                        onClose: () => {},
                      });
                    }}
                  >
                    Pay in Naira
                  </Button>

                  <Button
                    disabled={!validateForm()}
                    style={{
                      backgroundColor: Colors.BES_PURPLE,
                      height: 53,
                      width: 200,
                      margin: "0 auto",
                      border: "none",
                      marginBottom: 5,
                    }}
                    onClick={(e) => {
                      handleFlutterPaymentDollar({
                        callback: (response) => {
                          saveTransaction(response, order?.id);
                          closePaymentModal();
                        },
                        onClose: () => {},
                      });
                    }}
                  >
                    Pay in USD
                  </Button>
                </Row>
                <Row>
                  <button
                    style={{
                      backgroundColor: "#fff",
                      width: 200,
                      color: Colors.BES_RED,
                      fontSize: 13,
                      margin: "0 auto",
                      marginBottom: 20,
                      border: "none",
                    }}
                    onClick={handleModalShow}
                  >
                    Pay with Bank Transfer
                  </button>
                </Row>
              </Col>
            </Row>
          ) : (
            <Row style={{ height: "100%" }}>
              <Col lg={6} style={{ marginTop: 70 }}>
                <h4 style={{ width: 460, fontWeight: 600 }}>Cart Details</h4>
                <OrderItem order={order} />
              </Col>
              <Col lg={4} style={{ margin: "90px auto" }}>
                <Row className="mt-3">
                  <Col>
                    <p style={styles.checkoutLabels}>Subtotal</p>
                    <p style={styles.checkoutLabels}>Shipping fee</p>
                    <p style={styles.checkoutLabels}>Handling fee</p>
                    <p style={styles.checkoutLabels}>Tax & Duties</p>
                    {order?.give_discount &
                    (order?.discount_amount !== null) ? (
                      <p style={styles.checkoutLabels}>Discount</p>
                    ) : null}
                    {order?.discount_claimed === "YES" && (
                      <p style={styles.checkoutLabels}>Discount</p>
                    )}
                  </Col>
                  <Col>
                    <p style={styles.checkoutValues}>
                      {clean_dollar_format(order?.amount)}
                    </p>
                    <p style={styles.checkoutValues}>
                      {clean_dollar_format(order?.shipping_fee)}
                    </p>
                    <p style={styles.checkoutValues}>
                      {clean_dollar_format(order?.handling_fee)}
                    </p>
                    <p style={styles.checkoutValues}>
                      {clean_dollar_format(order?.tax_duties)}
                    </p>
                    {order?.give_discount &
                    (order?.discount_amount !== null) ? (
                      <p style={{ color: "red", textAlign: "end" }}>
                        - {clean_dollar_format(order?.discount_amount)}
                      </p>
                    ) : null}
                    {order?.discount_claimed === "YES" && (
                      <p style={{ color: "red", textAlign: "end" }}>
                        - {clean_dollar_format(order?.discount_amount)}
                      </p>
                    )}
                  </Col>
                </Row>

                    {order?.give_discount &
                    (order?.discount_amount !== null) ? (
                      <Row className="mt-3">
                        <Col>
                          <div style={styles.promoDiv}>
                            {order?.discount_code}
                          </div>
                        </Col>
                      </Row>
                    ) : null}

                  {order?.give_discount & (order?.discount_amount !== null) ? (
                <Row className="mt-5">
                      <Col lg={9}>
                        {/* <div style={{display: "flex", justifyContent: "space-between", alignItems: 'center'}}> */}
                        <Form onSubmit={handleSubmit} style={styles.signInForm}>
                          <Form.Group
                            size="lg"
                            controlId="promo-code"
                            style={{ width: 300 }}
                            className="form-group"
                          >
                            <Form.Label style={{ color: "green" }}>
                              {" "}
                              Enter code below to claim discount.
                            </Form.Label>
                            <Form.Control
                              placeholder="Discount code"
                              value={discountCode}
                              onChange={(e) => setDiscountCode(e.target.value)}
                              className="loginFormInput"
                              style={{ width: 250 }}
                            />
                          </Form.Group>
                        </Form>
                      </Col>
                      <Col lg={3}>
                        {isLoading & !hasError ? (
                          <Checkmark />
                        ) : (
                          <Button
                            type="submit"
                            disabled={!validateDiscountForm()}
                            style={{
                              fontWeight: 550,
                              background: Colors.BES_PURPLE,
                              border: "none",
                            }}
                            onClick={handleSubmit}
                          >
                            Claim
                          </Button>
                        )}
                      </Col>
                </Row>
                  ) : null}
                <hr />
                <Row>
                  <Col>
                    <h5 style={styles.checkoutLabels}>Total</h5>
                  </Col>
                  <Col>
                    <h5 style={styles.checkoutValues}>
                      {clean_dollar_format(order?.order_total)}
                    </h5>
                  </Col>
                  <span
                    className="mt-2"
                    style={{ ...styles.checkoutValues, color: Colors.BES_RED }}
                  >
                    Total amount in Naira:{" "}
                    {clean_naira_format(order?.order_total_naira)}
                  </span>
                </Row>
                <Row>
                  <Form.Group
                    className="mt-5 mb-3"
                    id="formGridCheckbox"
                    style={{ display: "inline-flex" }}
                  >
                    <Form.Check
                      type="checkbox"
                      // label="I accept the "
                      onChange={(e) => {
                        setAcceptConditions(e.target.checked);
                      }}
                    />
                    <button
                      className="form-check-label"
                      style={styles.termsAndConditionButton}
                      onClick={handleShow}
                    >
                      I accept the terms and conditions
                    </button>
                  </Form.Group>
                  <Button
                    disabled={!validateForm()}
                    style={{
                      backgroundColor: Colors.BES_PURPLE,
                      height: 53,
                      width: 200,
                      margin: "0 auto",
                      border: "none",
                      marginBottom: 10,
                    }}
                    onClick={(e) => {
                      handleFlutterPaymentNaira({
                        callback: (response) => {
                          saveTransaction(response, order?.id);
                          closePaymentModal();
                        },
                      });
                    }}
                  >
                    Pay in Naira
                  </Button>
                  <Button
                    disabled={!validateForm()}
                    style={{
                      backgroundColor: Colors.BES_PURPLE,
                      height: 53,
                      width: 200,
                      margin: "0 auto",
                      marginBottom: 10,
                      border: 'none'
                    }}
                    onClick={(e) => {
                      handleFlutterPaymentDollar({
                        callback: (response) => {
                          saveTransaction(response, order?.id);
                          closePaymentModal();
                        },
                      });
                    }}
                  >
                    Pay in USD
                  </Button>
                </Row>
                <Row>
                  <button
                    style={{
                      backgroundColor: "#fff",
                      width: 200,
                      color: Colors.BES_RED,
                      fontSize: 13,
                      margin: "0 auto",
                      marginBottom: 20,
                      border: "none",
                    }}
                    onClick={handleModalShow}
                  >
                    Pay with Bank Transfer
                  </button>
                </Row>
              </Col>
            </Row>
          )}
        </Container>
      </section>
    </>
  );
};

export default CheckOutPage;
