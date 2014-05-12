static int EventPresent (int *es, int m, int cb) {
	// Используется функцией Rules для облегчения кодирования
	int i ;
	for (i = cb - m + l; i <= cb; i++) {
		if (es[i]) return TRUE;
	}
	return FALSE;
}

static void Rules (float *opn, float *hi, float *lo, float *cls,
float *vol, float *oi, float *atr, int nb, int vl, float v2,
float v3, float v4, int *ans) {
	// Процедура определяет шаблоны правил, используемых
	// в генетическом процессе эволюции модели, основанной на правилах.
	// opn, hi, lo, cls — стандартные ценовые данные [l..nb]
	// vol, oi — объем и открытый интерес [l..nb]
	// nb — количество дней
	// vl, v2, v3, v4 — селектор правил и параметры
	// ans — выходные ценовые данные [l..nb]

	// локальные макрофункции
	#define LinearScale(х,a,b) ( (х)* ( (b)-(а))/1000.0+(а) )
	#define BiasedPosScale(х,а) (0 . 000001*(х)*(х)*(а))
	#define Compare(a,b,dir) (((dir)> = 0)?((a)>(b) ): (fa)<(b)))
	
	// локальные переменные
	static int lbl, lb2, per, cb, maxlb=100;
	static float thr, fac, thr2, thrl, tmp, tiny=l.ОЕ-20;
	static int IsNewHigh[MAXBAR+l], IsNewLow[MAXBAR+l];
	static float Serl[MAXBAR+1] ;
	
	// шаблоны правил
	switch(vl) { // выбираем правило
		
		case 1: // сравнение изменения цены с порогом		
			lb1 = (int)BiasedPosScale(v2, 5 0 . 0 ) ;
			lb2 = (int)BiasedPosScale(v3, 5 0 . 0 ) ;
			fac = LinearScale(v4, - 2 . 5 , 2 . 5 ) * sqrt(abs(lbl - Ib2) > ;
			for (cb - maxlb; cb <= nb; cb++) {
				thr = fac * atr [cb];
				ans[cb] = cls[cb-lbl] - cls[cb-lb2] > thr;
			}
			break;
		
		case 2: // сравнение цены с простым скользящим средним
			per = 2 + (int)BiasedPosScale(v2, 48.0);
			Averages(Serl, cls, per, nb);
			for (cb = maxlb; cb <= nb; cb++) {
				ans[cb] = Compare(cls[cb], Serl[cb], V4-500.0);
			}
			break;

		case 3: // сравнение цены с экспоненциальным скользящим средним
			per = 2 + (int)BiasedPosScale(v2, 48.0);
			XAverageS(Serl, cls, per, nb) ;
			for (cb - maxlb; cb <= nb; cb++) {
				ans[cb] = Compare(cls[cb], Serl[cb], V4-500.0);
			}
			break;

		case 4: // сравнение падения открытого интереса с пороговым значением
			1b1 = 2 + (int)BiasedPosScale (v2, 48.0);
			thr = LinearScale(v3, 0.01, 0.50);
			for (cb=maxlb; cb<=nb; cb++) {
				tmp = (oi[cb-lbl] - oi[cb-l]) / (oi [cb-lbl] + tiny);
				ans [cb] = tmp > thr;
			}
			break;

		case 5: // сравнение увеличения открытого интереса с пороговым значением
			1b1 = 2 + (int) BiasedPosScale(v2, 48.0);
			thr = LinearScale(v3, 0.01, 0.99);
			for (cb = maxlb; cb <= nb; cb++) {
				tmp = (oi [cb-1] - oi[cb-lblj) / (oi [cb-lbl] + tiny) ;
				ans [cb] = tmp > thr;
			}
			break;

		case 6: // недавние новые максимумы
			1bl = 2 + (int)BiasedPosScale(v2, 48.0);
			1b2 = 1 + (int)BiasedPosScale(v3, 8.0);
			for (cb = lbl + 3; cb <= nb; cb++) {
				IsNewHigh[cb] = hi [cb] > Highest(hi, 1b1, cb-1);
			}
			for(cb - maxlb; cb <= nb; cb++) {
				ans[cb] = EventPresent(IsNewHigh, 1b2, cb);
			}
			break;

		case 7: // недавние новые минимумы
			1bl = 2 + (int)BiasedPosScale(v2, 48.0);
			1b2 = 1 + (int)BiasedPosScale(v3, 8.0);
			for (cb = lbl + 3; cb <= nb; cb++) {
				IsNewLow[cb] = lo[cb] < Lowest(lo, 1b1, cb-1) ;
			}
			for (cb = maxlb; cb <= nb; cb++) {
				ans[cb] = EventPresent(IsNewLow, 1b2, cb);
			}
			break;

		case 8: // среднее направленное движение
			thrl = LinearScale(v2, 5.0, 50.0);
			thr2 = thrl + LinearScale(v3, 5.0, 20.0);			
			AvgDirMov(hi, lo, cls, nb, 14, Serl);
			for (cb = maxlb; cb <= nb; cb++) {
				ans [cb] = (Serl[cb] > thrl && Serl [cb] < thr2)
				&& Compare (Serl[cb] , Serl[cb-l], v4-500.0);
			}	
			break;

		case 9: // Медленный %К
			thr = LinearScale(v2, 5.0, 95.0);
			fac = LinearScale(v3, 1.0, 20.0);
			thrl = thr - fac;
			thr2 = thr + fac;
			StochOsc(Serl, hi, lo, cls, 2, 10, nb) ;
			for (cb = maxlb; cb <= nb; cb++) {
				ans [cb] = (Serl[cb) > thrl && Serl [cb] < thr2)
				&& Compare(Serl[cb], Serl[cb-1], V4-500.0);
			}	
			break ;

		case 10: // направление наклона MACD
			lb1 = 2 + (int)BiasedPosScale(v2, 18.0);
			lb2 = lbl + 1 + (int)BiasedPosScale(v3, 48.0);
			MacdOsc(Serl, cls, 1, lbl, lb2, nb) ;
			for (cb = maxlb; cb <= nb; cb++) {
				ans[cb] = Compare(Serl[cb], Serl[cb-2], v 4 - 5 0 0 . 0 ) , •
			}
			break;
		
		default:
			nrerror("Undefined rule template selected");
			break;
	}
	
	// первые maxlb элементов результата должны иметь значение ЛОЖЬ
	memset (&ans [1] , 0, sizeof(*ans) * maxlb);
	
	#undef BiasedPosScale
	#undef LinearScale
}

static void Model (float *parms, float *dt, float *opn, float *hi,
float *lo, float *cls, float *vol, float *oi, float *dlrv, int nb,
TRDSIM &ts, float *eqcls) {
	// Генетическая эволюция модели входа, основанной на правилах.
	// File = xl6modOl.c
	// parms — набор [1..MAXPRM] параметров
	// dt — набор [1..nb] дат в формате ГГММДД
	// орn - набор [l..nb] цен открыти
	// hi — набор [l..nb] максимальных цен
	// 1о — набор [l..nb] минимальных цен
	// cls - набор [l..nb] цен закрытия
	// vol — набор [l..nb] значений объема
	// oi - набор [l..nb] значений открытого интереса
	// dlrv — набор [l..nb] средней долларовой волатильности
	// nb — количество дней в наборе данных
	// ts — ссылка на класс торгового симулятора
	// eqcls — набор [l..nb] уровней капитала при закрытых позициях

	// описываем локальные переменные
	static int rc, cb, ncontracts, maxhold, ordertype, signal;
	static int disp, k, modeltype;
	static float mmstp, ptlim, stpprice, limprice, tmp;
	static float exitatr[MAXBAR+1] ;
	static int rulel[MAXBAR+1], rule2[MAXBAR+1], rule3[MAXBAR+1];	

	// копируем параметры в локальные переменные для более удобного обращения к ним
	modeltype = parms[14];  // модель: 1=длинная позиция, 2=короткая
	ordertype = parms[15]; 	// вход: 1=на открытии, 2=по лимитному приказу,
							// 3=по стоп- приказу
	maxhold = 10; 			// максимальный период удержания позиции
	ptlim = 4; 				// целевая прибыль в единицах волатильности
	mmstp = 1; 				// защитная остановка в единицах волатильности

	// выполнение расчетов для всей ценовой информации
	AvgTrueRangeS(exitatr,hi,lo,cls,50,nb); // средний истинный диапазон для 
											// выхода
	switch(modeltype) {
		case 1: case 2: // для моделей открытия длинных и коротких позиций
			// для каждого дня отдельно оценить три правила
			Rules (opn, hi, lo, cls, vol, oi, exitatr, nb,
			parms[1], parms[2], parms[3], parms[4], rulel);
			Rules (opn, hi, lo, cls, vol, oi, exitatr, nb,
			parms[5] , parms[6] , parms[7] , parms[8] , rule2);
			Rules (opn, hi, lo, cls, vol, oi, exitatr, nb,
			parms[9] , parms[10] , parms[11] , parms[12] , rule3);
			break;
		default: 
			nrerror("Invalid model type");
	}

	// проходим через дни, чтобы моделировать настоящую торговлю
	for(cb = 1; cb <= nb; cb++) {
		
		// не открываем позиций до начала периода выборки
		//... то же самое, что установка MaxBarsBack в TradeStation
		if (dt[cb] < IS_DATE) { 
			eqcls[cb] = 0.0; continue; 
		}
		
		// выполняем все ожидающие приказы и сохраняем значение капитала по
		// закрытию
		rс = ts.update(opn[cb] , hi[cb], lo [cb], cls[cb], cb);
		if (rc != 0) nrerror("Trade buffer overflow");
		eqcls[cb] = ts.currentequity(EQ__CLOSETOTAL);
		
		// подсчитываем количество контрактов для торговли
		// ... мы хотим торговать долларовым эквивалентом волатильности
		// ... 2 новых контрактов S&P-500 на 12/31/98
		ncontracts - RoundToInteger(5673.О / dlrv[cb] ) ;
		if (ncontracts < 1) ncontracts = 1;
		
		// избегаем устанавливать приказы на дни с ограниченной торговлей
		if (hi[cb+l] == lo[cb+l]) continue;
		
		// генерируем входные сигналы, цены стоп- и лимитных приказов
		signal = 0;
		switch (modeltype) {
			case 1: // только длинные позиции
				if (rulel[cb] && rule2 [cb] && rule3[cb]) signal = 1;
				break;
			case 2: // только короткие позиции
				if (rulel[cb] && rule2 [cb] && rule3[cb]) signal = -1;
				break;
		}
		limprice = 0.5 * (hi[cb] + lo [cb]);
		stpprice = cls[cb] + 0.5 * signal * exitatr[cb] ;
		
		// открываем позицию, используя определенные типы приказов
		if (ts.position() <= 0 && signal == 1) {
			switch (ordertype) { // выбираем нужный тип приказа
				case 1: ts.buyopen('1', ncontracts); break;
				case 2: ts.buylimit('2', limprice, ncontracts); break;
				case 3: ts.buystop('3' , stpprice, ncontracts); break;
				default: nrerror("Invalid buy order selected");
			}
		} else if (ts.position() >= 0 && signal == -1) {
			switch(ordertype) { // выбираем нужный тип приказа
				case 1: ts.sellopen('4', ncontracts); break;
				case 2: ts.selllimit('5', limprice, ncontracts); break;
				case 3: ts.sellstop('6', stpprice, ncontracts); break;
				default: nrerror("Invalid sell order selected");
			}
		}
		// симулятор использует стандартную стратегию выхода
		tmp = exitatr[cb];
		ts.stdexitcls('X', ptlim*tmp, mmstp*tmp, maxhold);
		
	} // обрабатываем следующий день
}