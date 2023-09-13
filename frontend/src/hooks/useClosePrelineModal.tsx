import { useEffect } from 'react';

export const useClosePrelineModal = () => {
  useEffect(() => {
    const modalElement = document.querySelector("#hs-slide-down-animation-modal");
    console.log("the modal element",modalElement)
    if (window.HSOverlay && typeof window.HSOverlay.close === 'function' && modalElement) {
      window.HSOverlay.close(modalElement);
    }
  }, []);
}