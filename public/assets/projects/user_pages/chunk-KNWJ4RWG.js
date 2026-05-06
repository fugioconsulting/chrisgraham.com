import {
  init_checkbox_v1,
  init_radio_v1
} from "./chunk-73EB6NH7.js";
import {
  CF2Component,
  init_runtime,
  registerComponent
} from "./chunk-IF35HPMH.js";
import {
  __esm,
  init_define_process
} from "./chunk-XDBWEWVZ.js";

// projects/lib/packages/yggdrasil-blueprints/__generated__/blueprints/survey-image-option-v1.ts
var SurveyImageOptionV1;
var init_survey_image_option_v1 = __esm({
  "projects/lib/packages/yggdrasil-blueprints/__generated__/blueprints/survey-image-option-v1.ts"() {
    init_define_process();
    init_radio_v1();
    init_checkbox_v1();
    init_runtime();
    SurveyImageOptionV1 = class extends CF2Component {
      constructor(el, runtimeSel) {
        super(el, runtimeSel);
      }
      mount() {
        const inputElement = this.element.querySelector(".elSurveyImageOptionBase__Input").firstChild;
        const fireClickOnInput = () => {
          inputElement.click();
        };
        inputElement.addEventListener("click", fireClickOnInput);
        this.element.addEventListener("click", fireClickOnInput);
      }
    };
    registerComponent("SurveyImageOption/V1", SurveyImageOptionV1);
    window["SurveyImageOptionV1"] = SurveyImageOptionV1;
  }
});

export {
  init_survey_image_option_v1
};
//# sourceMappingURL=chunk-KNWJ4RWG.js.map
