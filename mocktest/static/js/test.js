// ---------------- TIMER LOGIC ---------------- //
// Timer setup (60 minutes = 3600 seconds)
let timeLeft = localStorage.getItem("remainingTime")
  ? parseInt(localStorage.getItem("remainingTime"))
  : 60 * 60;

function startTimer() {
  const timerDisplay = document.getElementById("timer");

  const timer = setInterval(() => {
    let minutes = Math.floor(timeLeft / 60);
    let seconds = timeLeft % 60;

    minutes = minutes < 10 ? "0" + minutes : minutes;
    seconds = seconds < 10 ? "0" + seconds : seconds;

    timerDisplay.innerText = `${minutes}:${seconds}`;

    // Save remaining time to localStorage
    localStorage.setItem("remainingTime", timeLeft);

    // Add color warnings
    if (timeLeft <= 60) {
      timerDisplay.classList.add("danger");
      timerDisplay.classList.remove("warning");
    } else if (timeLeft <= 600) {
      timerDisplay.classList.add("warning");
      timerDisplay.classList.remove("danger");
    } else {
      timerDisplay.classList.remove("warning", "danger");
    }

    // When time is up
    if (timeLeft <= 0) {
      clearInterval(timer);
      localStorage.removeItem("remainingTime");
      if (confirm("⏰ Time is up!\nDo you want to submit your test now?")) {
        submitTest();
      } else {
        alert("⚠️ Test will be auto-submitted anyway.");
        submitTest();
      }
    }

    timeLeft--;
  }, 1000);
}

window.onload = () => {
  startTimer();
};

// ✅ Clear localStorage on manual submit
function submitTest() {
  localStorage.removeItem("remainingTime");
  document.querySelector("form").submit();
}


// ---------------- QUESTION NAVIGATION + ANSWERS ---------------- //
let currentIndex = 0;
const totalQuestions = document.querySelectorAll('.question-box').length;

function showQuestion(index) {
  document.querySelectorAll('.question-box').forEach((box, i) => {
    box.style.display = i === index ? 'block' : 'none';
  });
  currentIndex = index;
}

function nextQuestion() {
  if (currentIndex < totalQuestions - 1) {
    showQuestion(currentIndex + 1);
  }
}

function clearResponse() {
  const radios = document.querySelectorAll(`#question-${currentIndex} input[type=radio]`);
  radios.forEach(r => r.checked = false);

  // also clear from localStorage
  if (radios.length > 0) {
    localStorage.removeItem(radios[0].name);
  }
}

// ✅ Save answer in localStorage
document.querySelectorAll('input[type=radio]').forEach(radio => {
  radio.addEventListener('change', function () {
    localStorage.setItem(this.name, this.value);
  });
});

// ✅ Restore answers on page load
window.addEventListener('load', function () {
  document.querySelectorAll('input[type=radio]').forEach(radio => {
    const savedValue = localStorage.getItem(radio.name);
    if (savedValue && radio.value === savedValue) {
      radio.checked = true;
    }
  });
});

// ---------------- RESTRICTIONS ---------------- //
// Disable refresh (F5, Ctrl+R)
document.addEventListener("keydown", function (e) {
  if ((e.key === "F5") || 
      (e.ctrlKey && e.key === "r") || 
      (e.ctrlKey && e.key === "R")) {
    e.preventDefault();
    alert("❌ Refresh is disabled during the test.");
  }
});

// Disable right-click
document.addEventListener("contextmenu", function (e) {
  e.preventDefault();
});

// Disable back button
history.pushState(null, null, location.href);
window.onpopstate = function () {
  history.go(1);
};
