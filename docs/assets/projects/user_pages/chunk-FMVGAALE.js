import {
  init_cf_utils,
  uuidv4
} from "./chunk-M4JGSF3Y.js";
import {
  __esm,
  __export,
  init_define_process
} from "./chunk-XDBWEWVZ.js";

// projects/user_pages/app/javascript/lander/utils/error_with_cause.ts
var CFErrorWithCause, getErrorCause, _stackWithCauses, CFstackWithCauses;
var init_error_with_cause = __esm({
  "projects/user_pages/app/javascript/lander/utils/error_with_cause.ts"() {
    init_define_process();
    CFErrorWithCause = class _CFErrorWithCause extends Error {
      constructor(message, options) {
        super(message);
        const cause = options?.cause ?? null;
        this.name = _CFErrorWithCause.name;
        if (cause) {
          this.cause = cause;
        }
        this.message = message;
      }
    };
    getErrorCause = (err) => {
      if (!err || typeof err !== "object" || !("cause" in err)) {
        return;
      }
      if (typeof err.cause === "function") {
        const causeResult = err.cause();
        return causeResult instanceof Error ? causeResult : void 0;
      } else {
        return err.cause instanceof Error ? err.cause : void 0;
      }
    };
    _stackWithCauses = (err, seen) => {
      if (!(err instanceof Error)) return "";
      const stack = err.stack || "";
      if (seen.has(err)) {
        return stack + "\ncauses have become circular...";
      }
      const cause = getErrorCause(err);
      if (cause) {
        seen.add(err);
        return stack + "\ncaused by: " + _stackWithCauses(cause, seen);
      } else {
        return stack;
      }
    };
    CFstackWithCauses = (err) => _stackWithCauses(err, /* @__PURE__ */ new Set());
    globalThis.CFErrorWithCause = CFErrorWithCause;
    globalThis.CFstackWithCauses = CFstackWithCauses;
  }
});

// projects/user_pages/app/javascript/lander/utils/path.ts
function pathJoin(...args) {
  if (args.length === 0) return "";
  const firstNotEmptyIndex = args.findIndex((arg) => arg?.length > 0);
  if (firstNotEmptyIndex === -1) return "";
  let result = args[firstNotEmptyIndex];
  for (let i = firstNotEmptyIndex + 1; i < args.length; i++) {
    const part = args[i] ?? "";
    if (part.length === 0) continue;
    let startChar = 0;
    while (startChar < part.length - 1 && part[startChar] === "/") {
      startChar += 1;
    }
    const shouldAddSlash = result.length > 0 && result[result.length - 1] !== "/";
    result += (shouldAddSlash ? "/" : "") + part.slice(startChar);
  }
  return result;
}
var init_path = __esm({
  "projects/user_pages/app/javascript/lander/utils/path.ts"() {
    init_define_process();
  }
});

// projects/user_pages/app/javascript/lander/utils/fetcher.ts
var fetcher_exports = {};
__export(fetcher_exports, {
  CFFetch: () => CFFetch,
  CFFetcherError: () => CFFetcherError,
  FetcherResponseErrorType: () => FetcherResponseErrorType,
  MANUALLY_ABORTED: () => MANUALLY_ABORTED,
  default: () => Fetcher,
  isBackendError: () => isBackendError,
  isFetcherError: () => isFetcherError,
  isResponseError: () => isResponseError
});
function isResponseError(response) {
  return response.fetcherErrorType != void 0;
}
function isFetcherError(response) {
  return response.fetcherErrorType == 0 /* Internal */;
}
function isBackendError(response) {
  return response.fetcherErrorType == 1 /* Backend */;
}
var CFFetcherErrorTypes, CFFetcherError, FetcherRequestDefaultOptions, FetcherResponseErrorType, MANUALLY_ABORTED, Fetcher, CFFetch;
var init_fetcher = __esm({
  "projects/user_pages/app/javascript/lander/utils/fetcher.ts"() {
    init_define_process();
    init_cf_utils();
    init_error_with_cause();
    init_path();
    CFFetcherErrorTypes = {
      NETWORK_ERROR: "NETWORK_ERROR",
      SERVER_ERROR: "SERVER_ERROR"
    };
    globalThis.CFFetcherErrorTypes = CFFetcherErrorTypes;
    CFFetcherError = class extends CFErrorWithCause {
      constructor(type, options) {
        super(type, options);
        this.name = "CFFetcherError";
        this.type = type;
      }
    };
    globalThis.CFFetcherError = CFFetcherError;
    FetcherRequestDefaultOptions = {
      retries: 1,
      timeoutMS: -1,
      timeoutAfterRetrial: 1e3,
      shouldCaptureServerError: false,
      convertThrowToErrorResponse: false,
      onlyOneInflightRequest: false,
      simulateNetworkError: false,
      canAbort: true
    };
    FetcherResponseErrorType = /* @__PURE__ */ ((FetcherResponseErrorType2) => {
      FetcherResponseErrorType2[FetcherResponseErrorType2["Internal"] = 0] = "Internal";
      FetcherResponseErrorType2[FetcherResponseErrorType2["Backend"] = 1] = "Backend";
      return FetcherResponseErrorType2;
    })(FetcherResponseErrorType || {});
    MANUALLY_ABORTED = "Manually aborted";
    Fetcher = class {
      constructor(options) {
        this.options = options || {};
        this.inflightRequests = {};
      }
      /*
       * This fetch call is an extension of original fetch which only fires
       * api with a loading state before and after the call.
       * Can also debounce greater or less than 500ms if required.
       * The fetch request returns the JSON promise and is abortable
       */
      async fetch(url, init, requestOptions) {
        const { callbackData, customEvent, ...enhancedFetchOptions } = {
          ...FetcherRequestDefaultOptions,
          ...this.options?.requestOptions ?? {},
          ...requestOptions ?? {}
        };
        const { onlyOneInflightRequest, canAbort } = enhancedFetchOptions;
        if (this.loading && onlyOneInflightRequest) {
          if (canAbort) {
            this.abort();
          } else {
            return { fetcherErrorType: 0 /* Internal */, error: "Another request is in progress" };
          }
        }
        const requestId = uuidv4();
        enhancedFetchOptions.requestId = requestId;
        const abortController = new AbortController();
        this.inflightRequests[requestId] = {
          manuallyAborted: false,
          abortController
        };
        let response;
        this.url = url;
        const { headers, method, credentials } = this.options ?? {};
        init = {
          ...{ method, credentials },
          ...init ?? {},
          signal: abortController.signal,
          headers: {
            ...headers,
            ...init.headers
          }
        };
        this.setLoading(true, callbackData, customEvent);
        try {
          if (enhancedFetchOptions?.simulateNetworkError) {
            throw new Error("Network Error");
          }
          response = await this.enhancedFetch(url, init, enhancedFetchOptions);
          this.setLoading(false, callbackData, customEvent);
          if (this.options.debug) {
            console.log("[Fetch Request Completed]", response);
          }
          return response;
        } catch (error) {
          this.setLoading(false, error, customEvent);
          let err = error;
          if (this.inflightRequests[requestId].manuallyAborted) {
            err = MANUALLY_ABORTED;
          } else {
            if (this.options.debug) {
              console.log("[Error During Fetch]", error);
            }
          }
          if (enhancedFetchOptions.convertThrowToErrorResponse) {
            return { fetcherErrorType: 0 /* Internal */, error: err };
          } else {
            throw err;
          }
        } finally {
          delete this.inflightRequests[requestId];
        }
      }
      async toJSON(response) {
        if (isResponseError(response)) {
          return response;
        } else {
          try {
            if (response.ok) {
              return await response.json();
            } else if ([400, 422].includes(response.status)) {
              return { fetcherErrorType: 1 /* Backend */, error: await response.json() };
            } else {
              throw new CFFetcherError(CFFetcherErrorTypes.SERVER_ERROR, {
                cause: new Error(
                  `Invalid response from server
  Status: ${response.status}
  Body: ${await response.text()}`
                )
              });
            }
          } catch (error) {
            if (this.options.requestOptions.convertThrowToErrorResponse) {
              return { fetcherErrorType: 0 /* Internal */, error };
            } else {
              throw error;
            }
          }
        }
      }
      async post(url, data, requestOptions, init) {
        const response = await this.fetch(
          url,
          {
            method: "POST",
            body: JSON.stringify(data),
            ...init ?? {}
          },
          requestOptions
        );
        return await this.toJSON(response);
      }
      async get(url, data, requestOptions, init) {
        let fullUrl = url;
        const queryParams = Object.entries(data ?? {}).filter(([, v]) => !!v).map(([k, v]) => `${k}=${v}`).join("&");
        if (queryParams) {
          fullUrl = `${fullUrl}?${queryParams}`;
        }
        const response = await this.fetch(
          fullUrl,
          {
            method: "GET",
            ...init ?? {}
          },
          requestOptions
        );
        return this.toJSON(response);
      }
      async enhancedFetch(url, init, opts) {
        const { retries, timeoutMS, timeoutAfterRetrial, shouldCaptureServerError, requestId } = opts;
        let lastErr;
        for (let i = 0; i < retries; i++) {
          try {
            if (i > 0) {
              await new Promise((resolve) => setTimeout(resolve, timeoutAfterRetrial));
            }
            if (shouldCaptureServerError) {
              return await this.fetchWithTimeout(url, init, timeoutMS, requestId).then((response) => {
                if (response.status >= 500) {
                  throw new CFFetcherError(CFFetcherErrorTypes.SERVER_ERROR);
                }
                return response;
              });
            } else {
              return await this.fetchWithTimeout(url, init, timeoutMS, requestId);
            }
          } catch (err) {
            if (err instanceof CFFetcherError && err.type == CFFetcherErrorTypes.SERVER_ERROR) {
              throw err;
            }
            lastErr = err;
          }
        }
        throw new CFFetcherError(CFFetcherErrorTypes.NETWORK_ERROR, { cause: lastErr });
      }
      fetchWithTimeout(url, init, timeoutDuration = 1e3, requestId) {
        if (timeoutDuration > 0) {
          setTimeout(() => this.abort(requestId), timeoutDuration);
        }
        if (url.startsWith("http") || url.startsWith("https")) {
          return fetch(url, init);
        } else {
          const finalUrl = pathJoin(this.options.pathPrefix, url);
          return fetch(finalUrl, init);
        }
      }
      abort(requestId) {
        const requestsToAborts = requestId ? [requestId] : Object.keys(this.inflightRequests) ?? [];
        requestsToAborts.forEach((key) => {
          const inflightRequest = this.inflightRequests[key];
          if (!inflightRequest) return;
          if (!inflightRequest?.manuallyAborted) {
            if (this.options.debug) {
              console.log(`[Aborting Request][RequestID=${key}]`, this.url);
            }
            inflightRequest.abortController.abort();
            inflightRequest.manuallyAborted = true;
          }
        });
      }
      setLoading(isLoading, details, customName) {
        let loadingEvent;
        const startEvent = customName && customName + "Started" || "CFFetchStarted";
        const endEvent = customName && customName + "Finished" || "CFFetchFinished";
        if (isLoading && !this.loading) {
          if (this.options.debug) {
            console.log("[Loading Started]", startEvent);
          }
          this.loading = true;
          loadingEvent = new CustomEvent(startEvent, {
            detail: details
          });
        } else if (!isLoading && this.loading) {
          if (this.options.debug) {
            console.log("[Loading Finished/Aborted]", endEvent);
          }
          this.loading = false;
          loadingEvent = new CustomEvent(endEvent, {
            detail: details
          });
        }
        if (loadingEvent) {
          document.dispatchEvent(loadingEvent);
        }
      }
    };
    globalThis.CFFetcher = globalThis.CFFetcher || Fetcher;
    CFFetch = async (url, data, requestOptions) => {
      const fetcher = new Fetcher();
      return await fetcher.fetch(url, data, requestOptions);
    };
    globalThis.CFFetch = CFFetch;
  }
});

export {
  CFErrorWithCause,
  CFstackWithCauses,
  init_error_with_cause,
  CFFetcherError,
  isResponseError,
  isFetcherError,
  isBackendError,
  MANUALLY_ABORTED,
  Fetcher,
  CFFetch,
  fetcher_exports,
  init_fetcher
};
//# sourceMappingURL=chunk-FMVGAALE.js.map
