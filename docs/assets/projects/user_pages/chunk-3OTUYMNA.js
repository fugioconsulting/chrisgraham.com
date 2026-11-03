import {
  IntlTel_initPhoneInput,
  init_cf_utils
} from "./chunk-M4JGSF3Y.js";
import {
  CF2Component,
  init_runtime,
  registerComponent
} from "./chunk-IF35HPMH.js";
import {
  __esm,
  init_define_process
} from "./chunk-XDBWEWVZ.js";

// projects/lib/packages/yggdrasil-blueprints/__generated__/blueprints/input-v1.ts
var InputV1;
var init_input_v1 = __esm({
  "projects/lib/packages/yggdrasil-blueprints/__generated__/blueprints/input-v1.ts"() {
    init_define_process();
    init_cf_utils();
    init_runtime();
    InputV1 = class extends CF2Component {
      constructor(el, runtimeSel) {
        super(el, runtimeSel);
      }
      mount() {
        this.input = this.element.querySelector(".elInput");
        this.re = /^(([^<>()[\]\.,;:#%\s@"]+(\.[^<>()[\]\.,;:#%\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
        if (this.input.getAttribute("name") === "shipping_zip") {
          this.input.setAttribute("maxlength", "10");
        }
        this.addInputListeners();
        if (this.isStandalonePhoneNumberInput()) {
          this.setupPhoneNumberInput();
        }
      }
      update() {
        if (this.input.value) {
          this.element.classList.add("hasValue");
        } else {
          this.element.classList.remove("hasValue");
        }
      }
      isStandalonePhoneNumberInput() {
        return this.input.getAttribute("name") === "phone_number" && !$(this.input).closest('[data-page-element="Checkout/V1"]').length && !$(this.input).closest('[data-page-element="Checkout/V2"]').length && !$(this.input).closest('[data-page-element="Survey/V1').length;
      }
      addInputListeners() {
        this.input.addEventListener("focus", () => {
          this.element.querySelector("[data-input-status-type]").innerHTML = "";
          this.element.classList.remove("elInputValid");
          this.element.classList.remove("elInputError");
          this.element.classList.remove("elInputWarning");
          this.element.classList.add("elInputFocused");
        });
        if (this.isStandalonePhoneNumberInput() && this.input.iti) {
          this.input.addEventListener("countrychange", () => {
            const newCountry = this.input.iti.getSelectedCountryData().iso2;
            document.querySelectorAll('[name="phone_number"]').forEach((s) => {
              if (s.iti) {
                s.iti.setCountry(newCountry);
              }
            });
          });
        }
        this.input.addEventListener("blur", () => {
          this.element.classList.remove("elInputFocused");
          this.update();
          if (this.input.getAttribute("name") === "phone_number" && this.input.iti) {
            document.querySelectorAll('[name="phone_number"]').forEach((s) => {
              if (s.iti) {
                s.iti.setCountry(this.input.iti.getSelectedCountryData().iso2);
                s.iti.setNumber(this.input.value);
              }
            });
          }
          if (this.input.classList.contains("required1") && this.element.matches(".elInputError")) {
            if (this.input.value === "") {
              return;
            } else {
              if (this.input.getAttribute("name") === "email") {
                const parsedEmail = $.trim(input.value);
                if (this.re.test(parsedEmail)) {
                  this.element.classList.add("elInputValid");
                  this.element.classList.remove("elInputError");
                }
              } else if (this.isStandalonePhoneNumberInput() && !window.intlTelInput.utils.isValidNumber(this.input.value)) {
                this.element.classList.remove("elInputValid");
                this.element.classList.add("elInputError");
              } else {
                this.element.classList.remove("elInputError");
                this.element.classList.add("elInputValid");
              }
            }
          }
        });
      }
      setupPhoneNumberInput() {
        IntlTel_initPhoneInput(this.input, {
          initialCountry: window.cfVisitorData?.country ?? "us"
        });
      }
    };
    registerComponent("Input/V1", InputV1);
    window["InputV1"] = InputV1;
  }
});

export {
  init_input_v1
};
//# sourceMappingURL=chunk-3OTUYMNA.js.map
