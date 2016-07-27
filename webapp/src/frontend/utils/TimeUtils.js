import Intervals from '../constants/Intervals';
import moment    from 'moment';

//moment.locale('es');

const DATE_FORMATS = {
    [Intervals.MONTH]: 'MMM YYYY',
    [Intervals.THREE_MONTHS]: 'MMM YYYY',
    [Intervals.SIX_MONTHS]: 'MMM YYYY',
    [Intervals.YEAR]: 'YYYY'
};

export default class TimeUtils {
    static timestampForHit(hit) {
        return moment(hit.time).locale('es').format('LL');
    }

    static formatHitDate(hit) {
        return moment(hit.time).locale('es').format('LL');
    }

    static formatHitTime(hit) {
        let ts = moment(hit.time).locale('es');
        let str = ts.format('HH.mm');

        if (hit.name === 'Presidente' && str === '00.00') {
            return '??.??';
        } else {
            return str;
        }
    }

    static formatIntervalLabel(str, interval) {
        return moment(str).locale('es').format(DATE_FORMATS[interval]);
    }
}
