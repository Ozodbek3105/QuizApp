/** @format */

document.addEventListener('DOMContentLoaded', function () {
  // ===================================
  // 1. ASOSIY O'ZGARUVCHILAR
  // ===================================
  const timerElement = document.getElementById('timer');
  const questionBlocks = document.querySelectorAll('.question-block');
  const nextButtons = document.querySelectorAll('.next-question-btn');
  const prevButtons = document.querySelectorAll('.prev-question-btn');
  const finalFinishButton = document.getElementById('final-finish-btn');
  const mainExamForm = document.getElementById('main-exam-form');

  // Yangi qo'shilgan tugmalar
  const checkAnswerButtons = document.querySelectorAll('.check-answer-btn');

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
          // Agar biror sabab bilan blok topilmasa (masalan, birinchi savol)
          break;
        }

        // Shu blokning "Javobni Qabul Qilish" tugmasini topamiz
        const checkBtn = targetBlock.querySelector('.check-answer-btn');

        if (checkBtn && !checkBtn.disabled) {
          // Agar tugma topilsa va u 'disabled' (bosilmagan) bo'lsa,
          // demak bu bizga kerakli savol. Loopni to'xtatamiz.
          foundUnanswered = true;
          break;
        }

        // Agar tugma bosilgan (disabled) bo'lsa, bu savolni o'tkazib yuboramiz
        // va undan oldingi savolni qidiramiz
        const prevButtonOnTarget =
          targetBlock.querySelector('.prev-question-btn');

        if (prevButtonOnTarget) {
          targetBlockId = prevButtonOnTarget.getAttribute('data-prev-id');
        } else {
          // Agar bu blokda "Oldingi Savol" tugmasi bo'lmasa (demak bu birinchi savol)
          // Loopni to'xtatamiz
          targetBlockId = null; // Loopni to'xtatish uchun
        }
      }

      // Agar javob berilmagan savol topilsa...
      if (foundUnanswered && targetBlock) {
        currentBlock.style.display = 'none';
        targetBlock.style.display = 'block';
        window.scrollTo({ top: 0, behavior: 'smooth' });
      } else {
        // Agar topilmasa (masalan, oldindagi barcha savollarga javob berilgan)
        // Shunchaki hech narsa qilmaymiz yoki xabar beramiz
        alert('Oldinda javob berilmagan savol qolmadi.');
        // Yoki birinchi savolga o'tish mumkin:
        // const firstBlock = document.getElementById('q_block_1');
        // currentBlock.style.display = 'none';
        // firstBlock.style.display = 'block';
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
      }, 500); // 500 millisekund = 0.5 soniya
      // ==================================================
    });
  });

  // ===================================
  // 4. VAQT HISOBLAGICH
  // ===================================

  let timeInSeconds = 60*60; // 55 daqiqa

  function updateTimer() {
    if (!timerElement) {
      clearInterval(timerInterval);
      return;
    }

    if (timeInSeconds <= 0) {
      clearInterval(timerInterval);
      timerElement.textContent = '00:00';
      alert('Vaqt tugadi! Imtihon avtomatik yakunlanadi.');
      if (mainExamForm) {
        mainExamForm.submit();
      }
      return;
    }

    const minutes = Math.floor(timeInSeconds / 60);
    const seconds = timeInSeconds % 60;
    timerElement.textContent = `${minutes.toString().padStart(2, '0')}:${seconds
      .toString()
      .padStart(2, '0')}`;

    // 5 daqiqa qolganda rangni o'zgartirish
    if (timeInSeconds <= 300) {
      timerElement.style.color = '#dc3545';
    }

    timeInSeconds--;
  }

  const timerInterval = setInterval(updateTimer, 1000);
  updateTimer(); // Darhol boshlanishi uchun

  // ===================================
  // 5. IMTIHONNI YAKUNLASH TUGMASI
  // ===================================

  if (finalFinishButton && mainExamForm) {
    finalFinishButton.addEventListener('click', function (event) {
      event.preventDefault();

      // Vaqt hisoblagichini to'xtatish
      clearInterval(timerInterval);

      // Tasdiqlash
      const isConfirmed = confirm(
        'Imtihonni yakunlashga ishonchingiz komilmi?'
      );

      if (isConfirmed) {
        mainExamForm.submit();
      } else {
        // Agar bekor qilinsa, timerni qayta boshlash
        const newTimerInterval = setInterval(updateTimer, 1000);
      }
    });
  }
});

// ===================================
// 6. JAVOBNI TEKSHIRISH FUNKSIYASI (YANGILANDI)
// ===================================

function checkAnswerFrontend(questionBlock, selectedAnswer, correctAnswer) {
  const allOptions = questionBlock.querySelectorAll('.option-label');
  const allRadios = questionBlock.querySelectorAll('input[type="radio"]');

  // === XATO TUZATILDI ===
  // Faqat tanlanmagan radio buttonlarni o'chirish.
  // Tanlangan javob (to'g'ri yoki noto'g'ri bo'lishidan qat'iy nazar)
  // serverga yuborilishi uchun `disabled=false` bo'lib qolishi SHART!
  allRadios.forEach((radio) => {
    if (!radio.checked) {
      radio.disabled = true; // Boshqa, tanlanmagan variantlarni o'chirish
    }
  });
  // ======================

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
