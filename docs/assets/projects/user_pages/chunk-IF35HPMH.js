import {
  __esm,
  __export,
  init_define_process
} from "./chunk-XDBWEWVZ.js";

// projects/user_pages/app/javascript/lander/runtime.ts
var runtime_exports = {};
__export(runtime_exports, {
  CF2Component: () => CF2Component,
  CF2ComponentSingleton: () => CF2ComponentSingleton,
  ForloopDrop: () => ForloopDrop,
  blank: () => blank,
  createComponentGroup: () => createComponentGroup,
  registerComponent: () => registerComponent
});
function registerComponent(name, klass) {
  componentByName[name] = klass;
  componentNameByClass[klass.name] = name;
}
function createComponentGroup(klass, components) {
  const groupObject = {};
  groupObject.on = (eventName, eventHandler) => {
    components.forEach((c) => {
      c.on(eventName, eventHandler);
    });
  };
  for (const propertyName of Object.getOwnPropertyNames(klass.prototype)) {
    if (!["constructor"].includes(propertyName)) {
      groupObject[propertyName] = (...args) => {
        components.forEach((c) => {
          klass.prototype[propertyName].apply(c, args);
        });
      };
    }
  }
  return groupObject;
}
function blank(value) {
  return value === false || value === null || typeof value === "undefined" || value === "";
}
function uuidv4() {
  return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, function(c) {
    const r = Math.random() * 16 | 0, v = c == "x" ? r : r & 3 | 8;
    return v.toString(16);
  });
}
var componentByName, componentNameByClass, CF2Component, ForloopDrop, CF2ComponentSingleton;
var init_runtime = __esm({
  "projects/user_pages/app/javascript/lander/runtime.ts"() {
    init_define_process();
    componentByName = {};
    componentNameByClass = {};
    CF2Component = class _CF2Component {
      constructor(element) {
        this.element = element;
        this.subscribers = {};
        this.id = Array.from(this.element.classList).find((c) => c.startsWith("id"));
        for (const propertyName of Object.getOwnPropertyNames(this.constructor.prototype)) {
          if (propertyName.startsWith("on")) {
            if (typeof this.constructor.prototype[propertyName] === "function") {
              this.subscribers[propertyName] = [];
              this[propertyName] = (...args) => {
                return this.subscribers[propertyName].map((eventHandler) => eventHandler.apply(this, args));
              };
            } else {
              console.error(
                // eslint-disable-next-line max-len
                `[Component=${this.constructor.name}] Method ${propertyName} is reserved for event listeners and should be defined as a empty function => on<EventName>() {}
  Got:
`,
                this.constructor.prototype[propertyName].toString()
              );
            }
          }
        }
        for (const dataName in this.element.dataset) {
          if (!dataName.startsWith("param")) {
            this[dataName] = this.element.dataset[dataName];
          }
        }
        const stateNodeData = _CF2Component.getStateNodeData(this.element);
        if (stateNodeData) {
          Object.assign(this, stateNodeData);
        }
        if (this.afterMount) {
          document.addEventListener("CF2:HydrateTreeInitialized", () => {
            this.afterMount();
          });
        }
      }
      static getStateNodeData(element) {
        const id = element.getAttribute("data-state-node-script-id");
        const stateNode = id && document.getElementById(id);
        if (id && stateNode) {
          return JSON.parse(stateNode.textContent);
        }
      }
      // eslint-disable-next-line
      mount(element) {
      }
      render() {
      }
      replaceContent(html) {
        const elementsToReplace = this.element.querySelectorAll("[ygg-render]");
        if (elementsToReplace.length > 0) {
          elementsToReplace.forEach((elementToReplace) => {
            const yggRenderAttr = elementToReplace.getAttribute("ygg-render");
            const span = document.createElement("span");
            span.innerHTML = html;
            const newRenderedElementInnerHTML = span.querySelector(`[ygg-render="${yggRenderAttr}"]`).innerHTML;
            this.element.querySelector(`[ygg-render="${yggRenderAttr}"]`).innerHTML = newRenderedElementInnerHTML;
          });
        } else {
          this.element.innerHTML = html;
        }
      }
      initialize() {
      }
      // TODO: Refactor getComponent and getComponents to receive a class instead of a string
      getComponent(klass) {
        const componentName = typeof klass === "string" ? klass : componentNameByClass[klass.name];
        return this.element.querySelector(`[data-page-element="${componentName}"]`)?.cf2_instance;
      }
      getClosestComponent(name) {
        return this.element.closest(`[data-page-element="${name}"]`)?.cf2_instance;
      }
      getComponents(name) {
        return Array.from(this.element.querySelectorAll(`[data-page-element="${name}"]`))?.map(
          (c) => c.cf2_instance
        );
      }
      getComponentGroup(klass, handlers) {
        const componentName = componentNameByClass[klass.name];
        const components = this.getComponents(componentName);
        const group = createComponentGroup(klass, components);
        if (handlers) {
          for (const handlerName in handlers) {
            group.on(handlerName, handlers[handlerName]);
          }
        }
        return group;
      }
      setHandlers(klass, handlers) {
        const componentName = componentNameByClass[klass.name];
        const components = this.getComponents(componentName);
        for (const c of components) {
          for (const handlerName in handlers) {
            c.on(handlerName, handlers[handlerName]);
          }
        }
      }
      getAllComponents() {
        const componentList = [];
        Array.from(this.element.querySelectorAll("[data-page-element]"))?.forEach((c) => {
          if (c.cf2_instance) componentList.push(c.cf2_instance);
        });
        return componentList;
      }
      on(eventName, eventHandler) {
        if (this.subscribers[eventName]) {
          this.subscribers[eventName].push(eventHandler);
        } else {
          console.warn(`Event ${eventName} not supported by ${this.constructor.name}`);
        }
      }
      // NOTE: Build components by firstly building inner elements, and then walking up tree.
      // As we need to move from the leaf nodes to parent nodes. It also accepts a list of old
      // components in which you can re-use components built from an old list.
      static hydrateTree(parentNode, options) {
        const scopeToYggRender = !!options?.scopeToYggRender;
        const selector = scopeToYggRender ? "[ygg-render] [data-page-element]" : "[data-page-element]";
        const nodes = (parentNode ?? document).querySelectorAll(selector);
        nodes.forEach((node) => {
          const closestPageElement = $(node.parentNode).closest("[data-page-element]")[0];
          if (closestPageElement == parentNode || closestPageElement == null) {
            const klassName = node.getAttribute("data-page-element").replace("/", "");
            const ComponentBuilder = window[klassName];
            if (ComponentBuilder) {
              node.cf2_instance = new ComponentBuilder(node);
              node.getComponent = () => node.cf2_instance;
              node.cf2_instance.initialize();
            }
            _CF2Component.hydrateTree(node);
            if (ComponentBuilder) {
              node.cf2_instance.mount();
            }
          }
        });
      }
    };
    globalThis.CF2Component = CF2Component;
    globalThis.CF2HydrateTreeInitialized = false;
    window.addEventListener("DOMContentLoaded", () => {
      if (!globalThis.CF2HydrateTreeInitialized) {
        CF2Component.hydrateTree();
        queueMicrotask(() => {
          document.dispatchEvent(new CustomEvent("CF2:HydrateTreeInitialized"));
        });
      }
      globalThis.CF2HydrateTreeInitialized = true;
    });
    globalThis.CF2Blank = blank;
    ForloopDrop = class {
      constructor(length) {
        this.i = 0;
        this.length = length;
      }
      next() {
        this.i++;
      }
      get index0() {
        return this.i;
      }
      get index() {
        return this.i + 1;
      }
      get first() {
        return this.i === 0;
      }
      get last() {
        return this.i === this.length - 1;
      }
      get rindex() {
        return this.length - this.i;
      }
      get rindex0() {
        return this.length - this.i - 1;
      }
    };
    globalThis.CF2ForloopDrop = ForloopDrop;
    globalThis.CF2Utils = globalThis.CF2Utils ?? {};
    globalThis.CF2Utils.uuidv4 = uuidv4;
    CF2ComponentSingleton = class {
      static getInstance() {
        if (this._instance) {
          return this._instance;
        }
        this._instance = new this();
        return this._instance;
      }
    };
  }
});

export {
  registerComponent,
  CF2Component,
  runtime_exports,
  init_runtime
};
//# sourceMappingURL=chunk-IF35HPMH.js.map
