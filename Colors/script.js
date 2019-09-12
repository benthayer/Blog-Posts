
function myFunction(button) {
    // We've decided which button is more yellow. Update best guess and test values to match
    var button1 = document.getElementById("button-1");
    var button2 = document.getElementById("button-2");
    if (button == 1) {
        button = button1;
    } else {
        button = button2;
    }

    var colorElement = document.getElementById("color");
    var oldColor = getColorArray(colorElement);
    var updateColor = getColorArray(button);
    var newColor = mergeVecs(oldColor, updateColor, 0.5);

    color.style.backgroundColor = rgbString(newColor);

    // https://www.rapidtables.com/convert/color/hsv-to-rgb.html

    var diff = getDifferential(30);

    var guess1 = addVecs(newColor, diff);
    var guess2 = addVecs(newColor, diff.map(x => -x));
    // button1.style.backgroundColor = rgbString(guess1);
    // button2.style.backgroundColor = rgbString(guess2);
    button1.style.backgroundColor = rgbString(newColor);
    button2.style.backgroundColor = rgbString(guess1);
}

function getDifferential(lr) {
    // lr: the learning rate
    // returns: random vector whose 1-norm is lr

    // imagine there are space spaces, pick the location of two dividers.
    // The number of spaces between the dividers are the values for r, g, and b
    var space = lr + 2;
    var val1 = Math.floor(Math.random() * space);
    var val2 = val1;
    while (val1 == val2) {
        val2 = Math.floor(Math.random() * space);
    }

    if (val1 > val2) {
        var temp = val1;
        val1 = val2;
        val2 = temp;
    }

    var diff = [
        val1,
        val2 - val1 - 1,
        space - val2 - 1
    ];

    // The differential can either be positive or negative
    for (var i = 0; i < 3; i++) {
        if (Math.random < 0.5) {
            diff[i] = diff[i] * -1;
        }
    }
    return diff;
}

function addVecs(vec1, vec2) {
    var newVec = new Array(vec1.length);
    for (var i = 0; i < vec1.length; i++) {
        newVec[i] = vec1[i] + vec2[i];
    }
    return newVec;
}

function mergeVecs(prev, update, origPct) {
    var temp = new Array(prev.length);
    for (var i = 0; i < prev.length; i++) {
        temp[i] = Math.round(origPct * prev[i] + (1 - origPct) * update[i]);
    }
    return temp;
}

function getColor(element) {
    return window.getComputedStyle(element, null).getPropertyValue('background-color');
}

function getColorArray(element) {
    var rgb = getColor(element);
    return rgb.substring(4, rgb.length - 1).replace(/ /g, '').split(',').map(x => parseInt(x, 10));
}

function rgbString(rgbArray) {
    return "rgb(" + rgbArray[0] + ", " + rgbArray[1] + ", " + rgbArray[2] + ")";
}