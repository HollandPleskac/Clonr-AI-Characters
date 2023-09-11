interface HSOverlayType {
    open: (element: Element) => void;
    close: (element: Element) => void;
}

interface Window {
    HSOverlay: HSOverlayType;
}


