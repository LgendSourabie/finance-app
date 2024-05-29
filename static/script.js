"use static";

function init() {
  defaultColor();
}

/**
 * when the app starts the stock overview option should be selected
 * and the button should be highlighted
 */
function defaultColor() {
  document.getElementById("option-0").style.backgroundColor =
    "rgb(71, 91, 232)";
}

/**
 * This is used to highlight the selected option the menu in links
 * @param {number} index : use to identified the Id of the index-th link
 */
function highlightSelection(index) {
  let selection = document.getElementById(`option-${index}`);
  removeHighlight();
  selection.style.backgroundColor = "rgb(71, 91, 232)";
}

/**
 * Before highlighting the clicked option all other option need to be not highlighted
 * @param {array} listArray : select all li elements and put them in an array
 */
function removeHighlight() {
  let allElements = document.querySelectorAll("li");
  for (let i = 0; i < allElements.length; i++) {
    const element = allElements[i];
    let selectedElement = document.getElementById(element.id);
    selectedElement.style.backgroundColor = "transparent";
  }
}
