import React from "react";
import { createNativeStackNavigator } from "@react-navigation/native-stack";
import { useAuth } from "../store/hooks";
import { MainScreen } from "../screens/MainScreen";
import LoginScreen from "../screens/LoginScreen";


const Stack = createNativeStackNavigator();

export function AppNavigator() {
    const { isLoggedIn } = useAuth();

    console.log('네비게이션 상태:', { isLoggedIn });

    return (
        <Stack.Navigator screenOptions={{headerShown: false}}>
            {isLoggedIn ? (<Stack.Screen name="Main" component={MainScreen} />) : (<Stack.Screen name="Login" component={LoginScreen}/>)}
        </Stack.Navigator>
    )
}