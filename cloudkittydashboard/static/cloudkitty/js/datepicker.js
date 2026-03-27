/**
 * CloudKitty Datepicker functionality
 * Handles date range selection with preset ranges and navigation
 */

function initDatepicker(options) {
    const {
        formId,
        startFieldName,
        endFieldName
    } = options;

    const $form = $('#' + formId);
    const $startInput = $('[name="' + startFieldName + '"]');
    const $endInput = $('[name="' + endFieldName + '"]');

    let lastClicked = sessionStorage.getItem('datepicker_lastClicked') || 'week';

    // Utility functions
    const formatDate = (date) => {
        return date.getFullYear() + '-' +
            String(date.getMonth() + 1).padStart(2, '0') + '-' +
            String(date.getDate()).padStart(2, '0');
    };

    const disableButtons = () => {
        $('.controls-container button').prop('disabled', true);
    };

    const submitForm = (startDate, endDate, periodType) => {
        $startInput.val(formatDate(startDate));
        $endInput.val(formatDate(endDate));
        lastClicked = periodType;
        sessionStorage.setItem('datepicker_lastClicked', lastClicked);
        $form.submit();
    };

    // Date calculation functions
    const dateCalculators = {
        day: {
            current: () => {
                const date = new Date();
                return { start: new Date(date), end: new Date(date) };
            },
            yesterday: () => {
                const date = new Date();
                date.setDate(date.getDate() - 1);
                return { start: new Date(date), end: new Date(date) };
            }
        },
        week: {
            current: () => {
                const start = new Date();
                start.setDate(start.getDate() - start.getDay() + 1);
                const end = new Date(start);
                end.setDate(start.getDate() + 6);
                return { start, end };
            },
            last: () => {
                const today = new Date();
                const currentWeekStart = new Date(today);
                currentWeekStart.setDate(today.getDate() - today.getDay() + 1);

                const start = new Date(currentWeekStart);
                start.setDate(currentWeekStart.getDate() - 7);

                const end = new Date(start);
                end.setDate(start.getDate() + 6);

                return { start, end };
            }
        },
        month: {
            current: () => {
                const today = new Date();
                const start = new Date(today.getFullYear(), today.getMonth(), 1);
                const end = new Date(today.getFullYear(), today.getMonth() + 1, 0);
                return { start, end };
            },
            last: (amount = 1) => {
                const end = new Date();
                end.setDate(0);
                const start = new Date();
                start.setMonth(end.getMonth() - (amount - 1), 1);
                return { start, end };
            }
        },
        year: {
            current: () => {
                const year = new Date().getFullYear();
                return {
                    start: new Date(year, 0, 1),
                    end: new Date(year, 11, 31)
                };
            },
            last: () => {
                const year = new Date().getFullYear() - 1;
                return {
                    start: new Date(year, 0, 1),
                    end: new Date(year, 11, 31)
                };
            }
        }
    };

    // Navigation functions
    const navigate = (direction) => {
        if (!$startInput.val() || !$endInput.val()) return;

        const currentStart = new Date($startInput.val());
        const currentEnd = new Date($endInput.val());
        const multiplier = direction === 'next' ? 1 : -1;

        const navigators = {
            day: () => {
                currentStart.setDate(currentStart.getDate() + multiplier);
                currentEnd.setDate(currentEnd.getDate() + multiplier);
            },
            week: () => {
                currentStart.setDate(currentStart.getDate() + (7 * multiplier));
                currentEnd.setDate(currentEnd.getDate() + (7 * multiplier));
            },
            month: () => {
                if (direction === 'next') {
                    currentStart.setMonth(currentStart.getMonth() + 1, 1);
                    currentEnd.setMonth(currentEnd.getMonth() + 2, 0);
                } else {
                    currentStart.setMonth(currentStart.getMonth() - 1, 1);
                    currentEnd.setMonth(currentEnd.getMonth(), 0);
                }
            },
            last3Month: () => {
                if (direction === 'next') {
                    currentStart.setMonth(currentStart.getMonth() + 3, 1);
                    currentEnd.setMonth(currentEnd.getMonth() + 4, 0);
                } else {
                    currentStart.setMonth(currentStart.getMonth() - 3, 1);
                    currentEnd.setMonth(currentEnd.getMonth() - 2, 0);
                }
            },
            last6Month: () => {
                if (direction === 'next') {
                    currentStart.setMonth(currentStart.getMonth() + 6, 1);
                    currentEnd.setMonth(currentEnd.getMonth() + 7, 0);
                } else {
                    currentStart.setMonth(currentStart.getMonth() - 6, 1);
                    currentEnd.setMonth(currentEnd.getMonth() - 5, 0);
                }
            },
            year: () => {
                currentStart.setFullYear(currentStart.getFullYear() + multiplier);
                currentEnd.setFullYear(currentEnd.getFullYear() + multiplier);
            }
        };

        if (navigators[lastClicked]) {
            navigators[lastClicked]();
            submitForm(currentStart, currentEnd, lastClicked);
        }
    };

    // Event handlers
    $('.dropdown-content button[data-period]').on('click', function () {
        disableButtons();

        const period = $(this).data('period');
        const view = $(this).data('view');
        const amount = $(this).data('amount') || 1;

        const { start, end } = dateCalculators[period][view](amount);
        const periodType = amount > 1 ? `last${amount}Month` : period;

        submitForm(start, end, periodType);
    });

    $('.arrow-btn').on('click', function () {
        disableButtons();
        navigate($(this).data('direction'));
    });
}
