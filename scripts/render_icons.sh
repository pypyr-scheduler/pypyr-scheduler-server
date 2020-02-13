#! env sh
RSVG_CONVERT=$(which rsvg-convert) || { echo "rsvg-convert seems not to be installed. Look for the package 'librsvg2-bin'." ; exit 127; }
for DIM in 48 72 96 144 192 500; do
    ${RSVG_CONVERT} -w ${DIM} -h ${DIM} -o logo-${DIM}.png logo.svg
done
