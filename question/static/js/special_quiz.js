/** @format */
// ===================================
// BU FAYL FAQAT special_quiz.html UCHUN
// (VAQT HISOBLAGICHSIZ VERSIYA)
// ===================================

document.addEventListener('DOMContentLoaded', function () {
  // ===================================
  // 1. ASOSIY O'ZGARUVCHILAR
  // ===================================
  // const timerElement = document.getElementById('timer'); // <-- Olib tashlandi
  const questionBlocks = document.querySelectorAll('.question-block');
  const nextButtons = document.querySelectorAll('.next-question-btn');
  const prevButtons = document.querySelectorAll('.prev-question-btn');
  const finalFinishButton = document.getElementById('final-finish-btn');
  const mainExamForm = document.getElementById('main-exam-form');

  // Yangi qo'shilgan tugmalar
  const checkAnswerButtons = document.querySelectorAll('.check-answer-btn');

  // Natija oynasi elementlari
  const resultOverlay = document.getElementById('result-overlay');
  const scoreDisplay = document.getElementById('score-display');
  const restartQuizBtn = document.getElementById('restart-quiz-btn');

  // ===================================
  // 2. SAVOLLAR NAVIGATSIYASI
  // ===================================

  // Barcha savollarni yashirish, faqat birinchisini ko'rsatish
  questionBlocks.forEach((block, index) => {
    if (index !== 0) {
      block.style.display = 'none';
    } else {
      block.style.display = 'block'; // Birinchisini ko'rsatish
    }
  });

  // KEYINGI SAVOL tugmalari
  nextButtons.forEach((btn) => {
    btn.addEventListener('click', function (event) {
      event.preventDefault();
      const nextId = this.getAttribute('data-next-id');
      const currentBlock = this.closest('.question-block');

      currentBlock.style.display = 'none';
      document.getElementById(nextId).style.display = 'block';
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  });

  // OLDINGI SAVOL tugmalari (O'ZGARTIRILDI)
  prevButtons.forEach((btn) => {
    btn.addEventListener('click', function (event) {
      event.preventDefault();

      const currentBlock = this.closest('.question-block');
      let targetBlockId = this.getAttribute('data-prev-id');
      let targetBlock = null;
      let foundUnanswered = false;

      // Loop orqali javob berilmagan oldingi savolni topamiz
      while (targetBlockId) {
        targetBlock = document.getElementById(targetBlockId);

        if (!targetBlock) {
          break;
        }

        // Shu blokning "Javobni Qabul Qilish" tugmasini topamiz
        const checkBtn = targetBlock.querySelector('.check-answer-btn');

        if (checkBtn && !checkBtn.disabled) {
          foundUnanswered = true;
          break;
        }

        const prevButtonOnTarget =
          targetBlock.querySelector('.prev-question-btn');

        if (prevButtonOnTarget) {
          targetBlockId = prevButtonOnTarget.getAttribute('data-prev-id');
        } else {
          targetBlockId = null;
        }
      }

      if (foundUnanswered && targetBlock) {
        currentBlock.style.display = 'none';
        targetBlock.style.display = 'block';
        window.scrollTo({ top: 0, behavior: 'smooth' });
      } else {
        alert('Oldinda javob berilmagan savol qolmadi.');
      }
    });
  });

  // ==========================================================
  // 3. JAVOBNI TEKSHIRISH (O'ZGARTIRILDI)
  // ==========================================================

  checkAnswerButtons.forEach((btn) => {
    btn.addEventListener('click', function (event) {
      event.preventDefault();

      const questionBlock = this.closest('.question-block');
      const correctAnswer = questionBlock.getAttribute('data-correct-answer');

      // Shu blokdagi tanlangan radio buttonni topish
      const selectedRadio = questionBlock.querySelector(
        'input[type="radio"]:checked'
      );

      if (!selectedRadio) {
        alert('Iltimos, avval biror variantni tanlang.');
        return;
      }

      const selectedValue = selectedRadio.value;

      // Javobni tekshirish funksiyasini chaqirish
      checkAnswerFrontend(questionBlock, selectedValue, correctAnswer);

      // Tugmani o'chirish (qayta bosishni oldini olish)
      this.disabled = true;
      this.textContent = 'Javob Qabul Qilindi';

      // === 4 SONIYA KUTISH VA KEYINGI SAVOLGA O'TISH ===
      const nextButton = questionBlock.querySelector('.next-question-btn');

      // 4 soniyadan so'ng keyingi savolga o'tish
      setTimeout(() => {
        if (nextButton) {
          // Agar "Keyingi Savol" tugmasi mavjud bo'lsa, uni bosamiz
          nextButton.click();
        } else {
          // Agar bu oxirgi savol bo'lsa (keyingi tugma yo'q)
          // Yakunlash tugmasiga e'tiborni qaratamiz
          if (finalFinishButton) {
            finalFinishButton.scrollIntoView({
              behavior: 'smooth',
              block: 'center',
            });
            // Uni biroz ajratib ko'rsatish (animation)
            finalFinishButton.style.transform = 'scale(1.05)';
            setTimeout(() => {
              finalFinishButton.style.transform = 'scale(1)';
            }, 1000);
          }
        }
      }, 500); // 4000 millisekund = 4 soniya
      // ==================================================
    });
  });

  // ===================================
  // 4. VAQT HISOBLAGICH (OLIB TASHLANDI)
  // ===================================

  // (Bo'sh)

  // =========================================================
  // 5. IMTIHONNI YAKUNLASH (TAYMERSIZ)
  // =========================================================

  if (finalFinishButton) {
    finalFinishButton.addEventListener('click', function (event) {
      event.preventDefault();

      // Vaqt hisoblagichini to'xtatish (kerak emas)
      // clearInterval(timerInterval);

      // Tasdiqlash
      const isConfirmed = confirm(
        'Imtihonni yakunlashga ishonchingiz komilmi?'
      );

      if (isConfirmed) {
        calculateAndShowResults();
      } else {
        // Timerni qayta boshlash (kerak emas)
        // timerInterval = setInterval(updateTimer, 1000);
      }
    });
  }

  // Natijalarni hisoblash va ko'rsatish funksiyasi
  function calculateAndShowResults() {
    let score = 0;
    const totalQuestions = parseInt(
      document.getElementById('total_question_count').value,
      10
    );

    // Barcha savol bloklarini aylanib chiqish
    questionBlocks.forEach((block) => {
      const correctAnswer = block.getAttribute('data-correct-answer');
      const selectedRadio = block.querySelector('input[type="radio"]:checked');

      if (selectedRadio) {
        const userAnswer = selectedRadio.value;
        if (userAnswer === correctAnswer) {
          score++;
        }
      }
    });

    // Natijani modal oynaga yozish
    scoreDisplay.textContent = `${score} / ${totalQuestions}`;

    // Modal oynani ko'rsatish
    if (resultOverlay) {
      resultOverlay.style.display = 'flex';
    }
  }

  // Qayta boshlash tugmasi logikasi
  if (restartQuizBtn) {
    restartQuizBtn.addEventListener('click', function () {
      location.reload(); // Sahifani qayta yuklash
    });
  }
}); // DOMContentLoaded tugashi

// ===================================
// 6. JAVOBNI TEKSHIRISH FUNKSIYASI (O'ZGARMAGAN)
// ===================================

function checkAnswerFrontend(questionBlock, selectedAnswer, correctAnswer) {
  const allOptions = questionBlock.querySelectorAll('.option-label');
  const allRadios = questionBlock.querySelectorAll('input[type="radio"]');

  // Faqat tanlanmagan radio buttonlarni o'chirish.
  allRadios.forEach((radio) => {
    if (!radio.checked) {
      radio.disabled = true; // Boshqa, tanlanmagan variantlarni o'chirish
    }
  });

  // Har bir variantni tekshirish (rang berish uchun)
  allOptions.forEach((option) => {
    const radioInput = option.querySelector('input[type="radio"]');
    const radioValue = radioInput.value;

    // To'g'ri javobni yashil rangda ko'rsatish
    if (radioValue === correctAnswer) {
      option.classList.add('correct-answer');
    }

    // Agar foydalanuvchi noto'g'ri javob belgilagan bo'lsa, uni qizil rangda ko'rsatish
    if (radioValue === selectedAnswer && selectedAnswer !== correctAnswer) {
      option.classList.add('incorrect-answer');
    }
  });
}
