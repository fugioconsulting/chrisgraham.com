import {
  CF2Component,
  init_runtime,
  registerComponent
} from "./chunk-IF35HPMH.js";
import {
  __esm,
  init_define_process
} from "./chunk-XDBWEWVZ.js";

// projects/lib/packages/yggdrasil-blueprints/__generated__/blueprints/text-area-v1.ts
var TextAreaV1;
var init_text_area_v1 = __esm({
  "projects/lib/packages/yggdrasil-blueprints/__generated__/blueprints/text-area-v1.ts"() {
    init_define_process();
    init_runtime();
    TextAreaV1 = class extends CF2Component {
      constructor(el, runtimeSel) {
        super(el, runtimeSel);
      }
      mount() {
        this.textarea = this.element.querySelector(".elTextarea");
        const label = this.element.querySelector(".elLabel");
        this.addTextareaListeners(this.textarea);
        this.update();
      }
      update() {
        if (this.textarea.value) {
          this.textarea.classList.add("hasValue");
          this.element.classList.add("hasValue");
        } else {
          this.textarea.classList.remove("hasValue");
          this.element.classList.remove("hasValue");
        }
      }
      addTextareaListeners(textarea, re) {
        textarea.addEventListener("focus", () => {
          this.element.querySelector("[data-input-status-type]").innerHTML = "";
          this.element.classList.remove("elInputValid");
          this.element.classList.remove("elInputError");
          this.element.classList.remove("elInputWarning");
          this.element.classList.add("elInputFocused");
        });
        textarea.addEventListener("blur", () => {
          this.element.classList.remove("elInputFocused");
          this.update();
          if (textarea.classList.contains("required1") && textarea.value === "") {
            return;
          }
        });
      }
    };
    registerComponent("TextArea/V1", TextAreaV1);
    window["TextAreaV1"] = TextAreaV1;
  }
});

export {
  init_text_area_v1
};
//# sourceMappingURL=chunk-XIUAOK6S.js.map
