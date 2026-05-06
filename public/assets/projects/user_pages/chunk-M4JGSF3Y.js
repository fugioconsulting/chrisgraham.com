import {
  __esm,
  init_define_process
} from "./chunk-XDBWEWVZ.js";

// projects/lib/packages/yggdrasil/src/objectUtils.ts
function isNullOrUndefined(value) {
  return value === null || typeof value === "undefined";
}
var init_objectUtils = __esm({
  "projects/lib/packages/yggdrasil/src/objectUtils.ts"() {
    init_define_process();
  }
});

// projects/lib/packages/yggdrasil/src/cfLodash.ts
function isObject(value) {
  const type = typeof value;
  return value !== null && (type === "object" || type === "function");
}
function throttle(func, wait, options) {
  let leading = true;
  let trailing = true;
  if (typeof func !== "function") {
    throw new TypeError("Expected a function");
  }
  if (isObject(options)) {
    leading = "leading" in options ? !!options.leading : leading;
    trailing = "trailing" in options ? !!options.trailing : trailing;
  }
  return debounce(func, wait, {
    leading,
    trailing,
    maxWait: wait
  });
}
function debounce(func, wait, options) {
  let lastArgs;
  let lastThis;
  let maxWait;
  let result;
  let timerId;
  let lastCallTime;
  let lastInvokeTime = 0;
  let leading = false;
  let maxing = false;
  let trailing = true;
  if (typeof func !== "function") {
    throw new TypeError("Expected a function");
  }
  wait = +wait || 0;
  if (isObject(options)) {
    leading = !!options.leading;
    maxing = "maxWait" in options;
    maxWait = maxing ? Math.max(+options.maxWait || 0, wait) : maxWait;
    trailing = "trailing" in options ? !!options.trailing : trailing;
  }
  function invokeFunc(time) {
    const args = lastArgs;
    const thisArg = lastThis;
    lastArgs = lastThis = void 0;
    lastInvokeTime = time;
    result = func.apply(thisArg, args);
    return result;
  }
  function startTimer(pendingFunc, milliseconds) {
    return setTimeout(pendingFunc, milliseconds);
  }
  function cancelTimer(id) {
    clearTimeout(id);
  }
  function leadingEdge(time) {
    lastInvokeTime = time;
    timerId = startTimer(timerExpired, wait);
    return leading ? invokeFunc(time) : result;
  }
  function remainingWait(time) {
    const timeSinceLastCall = time - lastCallTime;
    const timeSinceLastInvoke = time - lastInvokeTime;
    const timeWaiting = wait - timeSinceLastCall;
    return maxing ? Math.min(timeWaiting, maxWait - timeSinceLastInvoke) : timeWaiting;
  }
  function shouldInvoke(time) {
    const timeSinceLastCall = time - lastCallTime;
    const timeSinceLastInvoke = time - lastInvokeTime;
    return lastCallTime === void 0 || timeSinceLastCall >= wait || timeSinceLastCall < 0 || maxing && timeSinceLastInvoke >= maxWait;
  }
  function timerExpired() {
    const time = Date.now();
    if (shouldInvoke(time)) {
      return trailingEdge(time);
    }
    timerId = startTimer(timerExpired, remainingWait(time));
    return void 0;
  }
  function trailingEdge(time) {
    timerId = void 0;
    if (trailing && lastArgs) {
      return invokeFunc(time);
    }
    lastArgs = lastThis = void 0;
    return result;
  }
  function cancel() {
    if (timerId !== void 0) {
      cancelTimer(timerId);
    }
    lastInvokeTime = 0;
    lastArgs = lastCallTime = lastThis = timerId = void 0;
  }
  function flush() {
    return timerId === void 0 ? result : trailingEdge(Date.now());
  }
  function pending() {
    return timerId !== void 0;
  }
  function debounced(...args) {
    const time = Date.now();
    const isInvoking = shouldInvoke(time);
    lastArgs = args;
    lastThis = this;
    lastCallTime = time;
    if (isInvoking) {
      if (timerId === void 0) {
        return leadingEdge(lastCallTime);
      }
      if (maxing) {
        timerId = startTimer(timerExpired, wait);
        return invokeFunc(lastCallTime);
      }
    }
    if (timerId === void 0) {
      timerId = startTimer(timerExpired, wait);
    }
    return result;
  }
  debounced.cancel = cancel;
  debounced.flush = flush;
  debounced.pending = pending;
  return debounced;
}
function isArrayEqual(array, compare) {
  if (array.length !== compare.length) return false;
  for (let i = 0; i < array.length; i++) {
    if (isObject(array[i])) {
      if (!isObjectEqual(array[i], compare[i])) {
        return false;
      }
    } else {
      if (array[i] !== compare[i]) {
        return false;
      }
    }
  }
  return true;
}
function isObjectEqual(obj1, obj2) {
  if (Array.isArray(obj1) && Array.isArray(obj2)) return isArrayEqual(obj1, obj2);
  if (!isObject(obj1) || !isObject(obj2)) {
    return false;
  }
  if (obj1 === obj2) {
    return true;
  }
  const item1Keys = Object.keys(obj1).sort();
  const item2Keys = Object.keys(obj2).sort();
  if (!isArrayEqual(item1Keys, item2Keys)) {
    return false;
  }
  return item2Keys.every((key) => {
    const value = obj1[key];
    const nextValue = obj2[key];
    if (isObject(obj1[key])) {
      return isObjectEqual(obj1[key], obj2[key]);
    } else {
      if (value === nextValue) {
        return true;
      }
    }
    return Array.isArray(value) && Array.isArray(nextValue) && isArrayEqual(value, nextValue);
  });
}
function cleanupEmptyValues(obj) {
  const result = {};
  for (const key in obj) {
    const value = obj[key];
    if (isNullOrUndefined(value) || value === "") continue;
    if (Array.isArray(value) && value.length === 0) continue;
    result[key] = value;
  }
  return result;
}
var reEscapedHtml, reHasEscapedHtml, reRegExpChar, reHasRegExpChar, isEqual;
var init_cfLodash = __esm({
  "projects/lib/packages/yggdrasil/src/cfLodash.ts"() {
    init_define_process();
    init_objectUtils();
    reEscapedHtml = /&(?:amp|lt|gt|quot|#(0+)?(39|34));/g;
    reHasEscapedHtml = RegExp(reEscapedHtml.source);
    reRegExpChar = /[\\^$.*+?()[\]{}|]/g;
    reHasRegExpChar = RegExp(reRegExpChar.source);
    isEqual = (value1, value2) => {
      if (isObject(value1) && isObject(value2)) {
        return isObjectEqual(value1, value2);
      }
      return value1 === value2;
    };
  }
});

// projects/user_pages/app/javascript/lander/cf_utils.ts
function uuidv4() {
  return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, function(c) {
    const r = Math.random() * 16 | 0, v = c == "x" ? r : r & 3 | 8;
    return v.toString(16);
  });
}
function IntlTel_initPhoneInput(inputElement, options = {}) {
  options = cleanupEmptyValues(options);
  const iti = window.intlTelInput(inputElement, {
    autoPlaceholder: "aggressive",
    countryOrder: ["us", "ca", "gb", "ie", "ai", "nz"],
    // TODO: I think the intialCountry logic should be placed in here
    // - First try to get the country from garlic
    // - Second from cfVisitorData
    // - Third from the browser
    // - Fourth falls back to US
    initialCountry: "us",
    countrySearch: false,
    fixDropdownWidth: false,
    // NOTE: This follows the docs recommendation to load utils script separately
    // @ts-expect-error - dynamic import from CDN URL
    loadUtils: () => import("https://cdnjs.cloudflare.com/ajax/libs/intl-tel-input/25.5.2/build/js/utils.min.js"),
    ...options
  });
  inputElement.iti = iti;
  return iti.promise;
}
function isEventInside(event, element) {
  return event.target === element || element.contains(event.target);
}
function closeOnClickOutside(element, cb) {
  document.addEventListener(
    "click",
    (evt) => {
      if (evt.target !== element && !element.contains(evt.target)) {
        cb();
      }
    },
    { capture: true }
  );
}
function range(min, max, step = 1) {
  let arraySize = Math.floor((max - min) / step);
  if (arraySize < 0) arraySize = 0;
  return new Array(arraySize).fill(0).map((_, index) => index * step + min);
}
function removePageScroll() {
  document.body.classList.add("remove-page-scroll");
}
function addPageScroll() {
  document.body.classList.remove("remove-page-scroll");
}
function isWithinCustomerCenterView() {
  const params = new URLSearchParams(window.location.search);
  const previewDynamicSection = !!params.get("preview-dynamic-section");
  return previewDynamicSection && window.self !== window.parent;
}
var init_cf_utils = __esm({
  "projects/user_pages/app/javascript/lander/cf_utils.ts"() {
    init_define_process();
    init_cfLodash();
  }
});

export {
  throttle,
  isEqual,
  init_cfLodash,
  uuidv4,
  IntlTel_initPhoneInput,
  isEventInside,
  closeOnClickOutside,
  range,
  removePageScroll,
  addPageScroll,
  isWithinCustomerCenterView,
  init_cf_utils
};
//# sourceMappingURL=chunk-M4JGSF3Y.js.map
