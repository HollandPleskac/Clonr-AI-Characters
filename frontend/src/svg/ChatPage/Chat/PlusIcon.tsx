type SvgIconProps = {
  svgClasses?: string;
  strokeClasses?: string;
};

export default function ExploreIcon({
  svgClasses,
  strokeClasses
}: SvgIconProps) {
  return (
    <svg
      width='16'
      height='16'
      viewBox='0 0 16 16'
      fill='none'
      xmlns='http://www.w3.org/2000/svg'
      className={svgClasses}
    >
      <path
        d='M2.66669 7.99984H13.3334M8.00002 2.6665V13.3332'
        className={strokeClasses}
        strokeWidth='1.8'
        strokeLinecap='round'
        strokeLinejoin='round'
      />
    </svg>
  );
}
