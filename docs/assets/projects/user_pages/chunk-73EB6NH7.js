import {
  CF2Component,
  init_runtime,
  registerComponent
} from "./chunk-IF35HPMH.js";
import {
  __esm,
  __publicField,
  init_define_process
} from "./chunk-XDBWEWVZ.js";

// projects/lib/packages/yggdrasil-blueprints/__generated__/blueprints/checkbox-v1.ts
var CheckboxV1;
var init_checkbox_v1 = __esm({
  "projects/lib/packages/yggdrasil-blueprints/__generated__/blueprints/checkbox-v1.ts"() {
    init_define_process();
    init_runtime();
    CheckboxV1 = class extends CF2Component {
      constructor(el, runtimeSel) {
        super(el, runtimeSel);
        __publicField(this, "checkbox");
      }
      mount() {
        this.checkbox = this.element.querySelector(".elCheckboxInput");
        this.preventClickOnLabel = this.element.getAttribute("data-prevent-click-on-label");
        if (this.element.dataset.triggerClickOnWrapper == "true") {
          this.element.addEventListener("click", (e) => {
            if (e.target.closest("a")) return;
            e.preventDefault();
            this.toggle();
          });
        } else if (this.preventClickOnLabel == "true") {
          this.element.querySelector(".elCheckboxLabel").addEventListener("click", (e) => {
            if (e.target.closest("a")) return;
            e.preventDefault();
          });
          this.element.querySelector(".elCheckbox").addEventListener("click", (e) => {
            this.toggle();
          });
        } else {
          this.element.addEventListener("click", (evt) => {
            if (evt.target.closest("a")) return;
            evt.preventDefault();
            this.toggle();
          });
          this.checkbox.addEventListener("click", (e) => {
            e.preventDefault();
            e.stopPropagation();
          });
        }
        if (this.useCheckboxIcon) {
          const fakeCheckbox = this.element.querySelector(".elCheckbox");
          fakeCheckbox.addEventListener("click", () => {
            this.toggle();
          });
        }
      }
      toggle() {
        this.setChecked(!this.checkbox.checked);
      }
      setChecked(checked) {
        const event = new Event("change");
        this.checkbox.checked = checked;
        this.checkbox.dispatchEvent(event);
      }
    };
    registerComponent("Checkbox/V1", CheckboxV1);
    window["CheckboxV1"] = CheckboxV1;
  }
});

// projects/lib/packages/yggdrasil-blueprints/__generated__/blueprints/radio-v1.ts
var RadioV1;
var init_radio_v1 = __esm({
  "projects/lib/packages/yggdrasil-blueprints/__generated__/blueprints/radio-v1.ts"() {
    init_define_process();
    init_runtime();
    RadioV1 = class extends CF2Component {
      constructor(el, runtimeSel) {
        super(el, runtimeSel);
      }
      mount() {
        const radioInput = this.element.querySelector(".elRadioInput");
        if (this.element.dataset.triggerClickOnWrapper == "true") {
          this.element.addEventListener("click", (e) => {
            if (e.target.closest("a")) return;
            e.preventDefault();
            this.enableRadio(radioInput);
          });
        }
      }
      enableRadio(radio) {
        const event = new Event("change");
        if (!radio.checked) radio.checked = true;
        radio.dispatchEvent(event);
      }
    };
    registerComponent("Radio/V1", RadioV1);
    window["RadioV1"] = RadioV1;
  }
});

export {
  init_checkbox_v1,
  init_radio_v1
};
//# sourceMappingURL=chunk-73EB6NH7.js.map
