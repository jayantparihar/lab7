import React, { useEffect, useState } from 'react'
import '../App.css';

export default function HealthStats() {
    const [isLoaded, setIsLoaded] = useState(false);
    const [stats, setStats] = useState({});
    const [error, setError] = useState(null)

	const getStats = () => {
	
        fetch(`http://acit3855.westus3.cloudapp.azure.com:8120/health/health`)
            .then(response => response.json())
            //.then(response => console.log(JSON.stringify(response)))
            .then((result)=>{
				console.log("Received Stats")
                setStats(result);
                setIsLoaded(true);
            },(error) =>{
                console.log(error)
                setError(error)
                setIsLoaded(true);
            })
    }
    useEffect(() => {
		const interval = setInterval(() => getStats(), 2000); // Update every 2 seconds
		return() => clearInterval(interval);
    }, [getStats]);

    if (error){
        return (<div className={"error"}>Error found when fetching from API</div>)
    } else if (isLoaded === false){
        return(<div>Loading...</div>)
    } else if (isLoaded === true){
        return(
            <div>
                <h1>Latest health Stats</h1>
                <table className={"StatsTable"}>
					<tbody>
						<tr>
							<td colSpan="2">Audit service status: {stats['audit']}</td>
                        </tr>
                        <tr>
							<td colSpan="2">Processing service status: {stats['processing']}</td>
						</tr>
						<tr>
							<td colSpan="2">Receiver service status: {stats['receiver']}</td>
						</tr>
						<tr>
							<td colSpan="2">Storage service status: {stats['storage']}</td>
						</tr>
                        <tr>
							<td colSpan="2">Last Updated: {stats['last_updated']}</td>
						</tr>
					</tbody>
                </table>
            </div>
        )
    }
}
