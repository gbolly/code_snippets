import { Colors } from "../../utils/styles";

const styles = {
  cartListHeader: {
    fontWeight: 600,
    fontSize: 16,
    color: "#22262A",
  },
  checkoutLabels: {
    textAlign: "left",
  },
  checkoutValues: {
    textAlign: "end",
  },
  termsAndConditionButton: {
    background: "none",
    border: "none",
    color: Colors.BES_PURPLE,
    cursor: "pointer",
    marginLeft: 5,
    marginTop: -2
  },
  promoDiv: {
    background: Colors.BES_PURPLE,
    borderRadius: 3,
    fontWeight: 600,
    color: "#ffff",
    width: "100%",
    height: 50,
    marginBottom: 20,
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    fontSize: 30,
    letterSpacing: 10,
  },
};

export default styles;
