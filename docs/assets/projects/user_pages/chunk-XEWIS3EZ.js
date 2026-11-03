import {
  addPageScroll,
  closeOnClickOutside,
  init_cf_utils,
  removePageScroll
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

// projects/lib/packages/yggdrasil-blueprints/__generated__/blueprints/modal-sidebar-v1.ts
var ModalSidebarV1;
var init_modal_sidebar_v1 = __esm({
  "projects/lib/packages/yggdrasil-blueprints/__generated__/blueprints/modal-sidebar-v1.ts"() {
    init_define_process();
    init_cf_utils();
    init_runtime();
    ModalSidebarV1 = class extends CF2Component {
      constructor(el, runtimeSel) {
        super(el, runtimeSel);
      }
      mount() {
        closeOnClickOutside(this.element.querySelector(".elModalSidebar"), () => this.hide());
      }
      show() {
        removePageScroll();
        this.element.classList.remove("forceHide");
        const wrapper = this.element.querySelector(".elModalSidebar");
        setTimeout(() => {
          wrapper.classList.add("elModalSidebarSlideAnimation");
        });
      }
      hide() {
        addPageScroll();
        this.element.classList.add("forceHide");
        const wrapper = this.element.querySelector(".elModalSidebar");
        wrapper.classList.remove("elModalSidebarSlideAnimation");
      }
    };
    registerComponent("ModalSidebar/V1", ModalSidebarV1);
    window["ModalSidebarV1"] = ModalSidebarV1;
  }
});

export {
  init_modal_sidebar_v1
};
//# sourceMappingURL=chunk-XEWIS3EZ.js.map
