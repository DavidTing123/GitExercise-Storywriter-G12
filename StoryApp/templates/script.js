let inputTextArea = document.getElementById("content");
let characCount = document.getElementById("charac-count");
let wordCount = document.getElementById("word-count");

inputTextArea.addEventListener("input", () => {
  characCount.textContent = inputTextArea.value.length;
  let txt = inputTextArea.value.trim();
  wordCount.textContent = txt.split(/\s+/).filter((item) => item).length;
});

let reachedTargets = {};

function updateWordCount() {
    const textInput = document.getElementById('content').value;
    const words = textInput.trim().split(/\s+/);
    const wordCount = words.length;

    const wordCountDisplay = document.getElementById('word-count');
    wordCountDisplay.textContent = `Word count: ${wordCount}`;

    
    const targets = [
        { count: 100, message: "Great job! You've reached 100 words." },
        { count: 200, message: "Congratulations! You've reached 200 words." },
        { count: 400, message: "Wow! You've reached 400 words." },
        { count: 650, message: "Amazing! You've reached 650 words." }
        
    ];

    
    for (const target of targets) {
        if (wordCount >= target.count && !reachedTargets[target.count]) {
            showPopup(target.message);
            reachedTargets[target.count] = true;
            break;
        }
    }

    
    if (!isAnyTargetReached(wordCount)) {
        hidePopup();
    }
}


function isAnyTargetReached(wordCount) {
    for (const targetCount in reachedTargets) {
        if (wordCount >= parseInt(targetCount) && reachedTargets[targetCount]) {
            return true;
        }
    }
    return false;
}


function showPopup(message) {
    const customPopup = document.getElementById('customPopup');
    const targetCountDisplay = document.getElementById('targetCountDisplay');
    targetCountDisplay.textContent = message;
    customPopup.style.display = 'block';

   
    document.getElementById('content').disabled = true;

    
    setTimeout(() => {
        hidePopup();
        document.getElementById('input-textarea').disabled = false; 
    }, 3000); 
}


function hidePopup() {
    const customPopup = document.getElementById('customPopup');
    customPopup.style.display = 'none';
}