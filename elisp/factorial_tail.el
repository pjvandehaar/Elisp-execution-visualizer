(defun factorial_tail (n acc)
  (if (= n 0)
      acc
    (factorial_tail (- n 1) (* acc n))))
(factorial_tail 5 1)
