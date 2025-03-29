def display_results(result: dict):
    """分析結果を表示する関数"""
    # レース情報の表示
    race_info = result.get('race_info', {})
    print(f"\n■ レース情報: {race_info.get('race_name', '不明')}")
    print(f"  競馬場: {race_info.get('track', '不明')} / {race_info.get('surface', '不明')} / {race_info.get('distance', '不明')}m")
    print(f"  馬場状態: {race_info.get('track_condition', '不明')}")
    print(f"  クラス: {race_info.get('grade', '不明')}")
    
    # レース特性の表示
    characteristics = race_info.get('race_characteristics', {})
    if characteristics:
        print("\n■ レース特性分析:")
        print(f"  波乱度: {characteristics.get('upset_likelihood', 0):.2f} (0-1)")
        print(f"  調子重要度: {characteristics.get('form_importance', 0):.2f} (0-1)")
        print(f"  ペース依存度: {characteristics.get('pace_dependency', 0):.2f} (0-1)")
        print(f"  クラス差: {characteristics.get('class_gap', 0):.2f} (0-1)")
    
    # 馬の分類を表示
    classified = result.get('classified_horses', {})
    if classified:
        print("\n■ 馬の分類:")
        
        # 本命馬の表示
        honmei = classified.get('honmei', [])
        if honmei:
            print("  【本命馬】")
            for horse in honmei:
                print(f"   {horse.get('horse_number', '?')}. {horse.get('horse_name', '不明')} " +
                      f"(オッズ:{horse.get('odds', '-'):.1f} / スコア:{horse.get('total_score', 0):.1f})")
        
        # 対抗馬の表示
        taikou = classified.get('taikou', [])
        if taikou:
            print("  【対抗馬】")
            for horse in taikou:
                print(f"   {horse.get('horse_number', '?')}. {horse.get('horse_name', '不明')} " +
                      f"(オッズ:{horse.get('odds', '-'):.1f} / スコア:{horse.get('total_score', 0):.1f})")
        
        # 穴馬の表示
        ana = classified.get('ana', [])
        if ana:
            print("  【穴馬】")
            for horse in ana:
                print(f"   {horse.get('horse_number', '?')}. {horse.get('horse_name', '不明')} " +
                      f"(オッズ:{horse.get('odds', '-'):.1f} / スコア:{horse.get('total_score', 0):.1f})")
    
    # 予測結果を表示
    predictions = result.get('predictions', [])
    if predictions:
        print("\n■ 予測順位:")
        for i, horse in enumerate(predictions[:5], 1):  # 上位5頭まで表示
            print(f"  {i}着: {horse.get('horse_number', '?')}. {horse.get('horse_name', '不明')} " +
                  f"(勝率:{horse.get('win_probability', 0):.1%})")
    
    # 馬券提案を表示
    betting_plan = result.get('betting_plan', {})
    if betting_plan:
        print("\n■ 馬券最適化プラン (予算:300円):")
        
        # 選択された戦略
        selected_strategy = betting_plan.get('selected_strategy', {})
        strategy_name = selected_strategy.get('strategy_name', '不明')
        print(f"  【推奨戦略】{strategy_name}")
        
        # 馬券内訳
        tickets = selected_strategy.get('tickets', [])
        if tickets:
            print("  【馬券内訳】")
            for ticket in tickets:
                bet_type = ticket.get('bet_type', '不明')
                horses_str = '-'.join(map(str, ticket.get('horses', [])))
                amount = ticket.get('amount', 0)
                expected_value = ticket.get('expected_value', 0)
                
                print(f"   {bet_type}: {horses_str} / {amount}円 (期待値:{expected_value:.2f})")
        
        # 総額
        total_amount = selected_strategy.get('total_amount', 0)
        total_expected_value = selected_strategy.get('total_expected_value', 0)
        print(f"  【総額】{total_amount}円 (総期待値:{total_expected_value:.2f})")


if __name__ == "__main__":
    main()
