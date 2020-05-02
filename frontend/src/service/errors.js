
const snakeToCamel = (str) => str.replace(
  /([-_][a-z])/g,
  (group) => group.toUpperCase()
    .replace('-', '')
    .replace('_', ''),
);


/**
 *
 * Function for handling errors returned by the api.
 * This function is being primarily used bý forms making a post request.
 *
 * The component will need to have the following structure:
 *      data() {
 *        form: {
 *          ...fields
 *        },
 *        formFeedback: {
 *          ...errFields
 *        }
 *      }
 *
 *      Every errField in errFields will need to have the name of the field as a prefix
 *      followed by either "Valid" or "ErrMsg".
 *
 * @param component
 * @param res
 * @param fieldMapping A dict containing names for the field with the corresponding api field name
 */
export function parseErrorsForm(component, res, fieldMapping) {
  const fields = component.form;

  if (fieldMapping === undefined) {
    fieldMapping = {};
  }

  if (component.formFeedback.errMessage === undefined) {
    console.error('Component does not have the formFeedback.errMessage field!');
    return;
  }

  component.formFeedback.isValid = false;
  component.formFeedback.errMessage = 'An unexpected error occurred!';

  if (res.constructor === Array) {
    [component.formFeedback.errMessage] = res;
  } else {
    Object.keys(res).forEach((key) => {
      let msg;

      if (res[key].constructor === Array) {
        [msg] = res[key];
      } else {
        msg = res[key];
      }

      component.formFeedback.errMessage = 'Please check the form fields'
                    + ' for more information what went wrong!';

      // Convert the key to camel as the backend uses django and python has the convention
      // of using snake case instead of camel but in vue we ue camel.
      key = snakeToCamel(key);

      if (fields.hasOwnProperty(key) || fieldMapping.hasOwnProperty(key)) {
        if (fieldMapping.hasOwnProperty(key)) {
          key = fieldMapping[key];
        }

        const kErrMsg = `${key}ErrMsg`;
        const kValid = `${key}Valid`;
        component.formFeedback[kErrMsg] = msg;
        component.formFeedback[kValid] = false;
      } else {
        component.formFeedback.errMessage = msg;
        // console.error(res);
        if (key !== 'nonFieldErrors') {
          console.error(`${key} has not been recognized as a field in the component!`);
        }
      }
    });
  }
}


/**
 * Resets for a given component all form errors and all error messages
 *
 */
export function resetFormErrors(component) {
  Object.keys(component.formFeedback).forEach((k) => {
    const v = component.formFeedback[k];

    if (typeof v === 'boolean') {
      component.formFeedback[k] = true;
    } else {
      component.formFeedback[k] = '';
    }
  });
}
