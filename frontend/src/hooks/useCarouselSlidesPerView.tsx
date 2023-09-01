'use client';

import { useEffect, useState } from "react";

interface SlidesPerViewOptions {
    normal: number;
    big: number;
}

export function useCarouselSlidesPerView() {
    const [slidesPerView, setSlidesPerView] = useState<SlidesPerViewOptions | null>(null)

    const updateSlidesPerView = () => {
        if (window.matchMedia('(min-width: 1400px)').matches) {
            setSlidesPerView({ normal: 6, big: 3 })
        } else if (window.matchMedia('(min-width: 1096px)').matches) {
            setSlidesPerView({ normal: 5, big: 3 })
        } else if (window.matchMedia('(min-width: 800px)').matches) {
            setSlidesPerView({ normal: 4, big: 2 })
        } else if (window.matchMedia('(min-width: 500px)').matches) {
            setSlidesPerView({ normal: 3, big: 1 })
        } else {
            setSlidesPerView({ normal: 2, big: 1 })
        }
    }

    useEffect(() => {
        updateSlidesPerView() // Call on mount to set the initial value
        window.addEventListener('resize', updateSlidesPerView) // Call on resize
    
        return () => {
          window.removeEventListener('resize', updateSlidesPerView)
        }
      }, [])

    return {
        slidesPerView: slidesPerView,
        isLoadingSlidesPerView: slidesPerView === null
    };
}
