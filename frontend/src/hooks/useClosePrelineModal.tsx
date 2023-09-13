import { useEffect } from 'react';

export const useClosePrelineModal = () => {
  useEffect(() => {
    const backdrop = document.querySelector('.hs-overlay-backdrop');
    console.log("the backdrop element",backdrop)
    if (backdrop) {
      backdrop.remove()
    }
  }, []);
}